import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .models import db, Performer, Studio, Scene, WantedScene, Config, FilteredScene
from .stash_api import StashAPI
from .stashdb_api import StashDBAPI
from .whisparr_api import WhisparrAPI

logger = logging.getLogger(__name__)

def run_discovery_task() -> Dict:
    """Main discovery task that finds new scenes"""
    logger.info("Starting scene discovery task")
    
    config = Config.get_config()
    if not config.discovery_enabled:
        logger.info("Discovery is disabled in configuration")
        return {'status': 'disabled', 'message': 'Discovery is disabled'}
    
    stash_api = StashAPI()
    stashdb_api = StashDBAPI()
    whisparr_api = WhisparrAPI()
    
    results = {
        'status': 'success',
        'new_scenes': 0,
        'filtered_scenes': 0,
        'wanted_added': 0,
        'errors': []
    }
    
    try:
        # Get monitored performers and studios
        monitored_performers = Performer.query.filter_by(monitored=True).all()
        monitored_studios = Studio.query.filter_by(monitored=True).all()
        
        logger.info(f"Monitoring {len(monitored_performers)} performers and {len(monitored_studios)} studios")
        
        # Process performers - limit to prevent timeouts
        performers_processed = 0
        max_performers_per_run = 10  # Limit to prevent worker timeout
        
        for performer in monitored_performers:
            if performers_processed >= max_performers_per_run:
                logger.info(f"Reached performer limit ({max_performers_per_run}) for this run")
                break
                
            try:
                performer_results = process_performer_scenes(performer, stashdb_api, stash_api, config)
                results['new_scenes'] += performer_results['new_scenes']
                results['filtered_scenes'] += performer_results['filtered_scenes']
                
                # Update last checked time
                performer.last_checked = datetime.utcnow()
                performers_processed += 1
                
                logger.info(f"Processed {performer.name}: {performer_results['new_scenes']} new, {performer_results['filtered_scenes']} filtered")
                
                # Commit progress periodically to prevent data loss
                if performers_processed % 5 == 0:
                    db.session.commit()
                    logger.info(f"Committed progress after {performers_processed} performers")
                
            except Exception as e:
                error_msg = f"Error processing performer {performer.name}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Process studios - limit to prevent timeouts
        studios_processed = 0
        max_studios_per_run = 5  # Studios have more scenes, so process fewer
        
        for studio in monitored_studios:
            if studios_processed >= max_studios_per_run:
                logger.info(f"Reached studio limit ({max_studios_per_run}) for this run")
                break
                
            try:
                studio_results = process_studio_scenes(studio, stashdb_api, stash_api, config)
                results['new_scenes'] += studio_results['new_scenes']
                results['filtered_scenes'] += studio_results['filtered_scenes']
                
                # Update last checked time
                studio.last_checked = datetime.utcnow()
                studios_processed += 1
                
                logger.info(f"Processed {studio.name}: {studio_results['new_scenes']} new, {studio_results['filtered_scenes']} filtered")
                
                # Commit progress after each studio due to large number of scenes
                db.session.commit()
                logger.info(f"Committed progress after studio {studio.name}")
                
            except Exception as e:
                error_msg = f"Error processing studio {studio.name}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Add wanted scenes to Whisparr using UUID-based method
        if config.auto_add_to_whisparr:
            try:
                wanted_results = add_wanted_scenes_to_whisparr(whisparr_api, config)
                results['wanted_added'] = wanted_results['added_count']
                results['whisparr_skipped'] = wanted_results.get('skipped_count', 0)
                if wanted_results.get('errors'):
                    results['errors'].extend(wanted_results['errors'])
            except Exception as e:
                error_msg = f"Error adding scenes to Whisparr: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Discovery completed: {results['new_scenes']} new scenes, {results['filtered_scenes']} filtered, {results['wanted_added']} added to Whisparr")
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Discovery task failed: {str(e)}"
        logger.error(error_msg)
        results['status'] = 'error'
        results['errors'].append(error_msg)
    
    return results

def process_performer_scenes(performer: Performer, stashdb_api: StashDBAPI, stash_api: StashAPI, config: Config) -> Dict:
    """Process ALL scenes for a specific performer, then filter locally"""
    logger.info(f"Getting ALL scenes for performer: {performer.name}")
    
    results = {'new_scenes': 0, 'filtered_scenes': 0}
    
    try:
        # Find performer in StashDB if not already linked
        if not performer.stashdb_id:
            stashdb_performers = stashdb_api.search_performer(performer.name)
            if stashdb_performers:
                # Try to match by name (simple matching for now)
                for sp in stashdb_performers:
                    if sp['name'].lower() == performer.name.lower():
                        performer.stashdb_id = sp['id']
                        break
        
        if not performer.stashdb_id:
            logger.warning(f"Could not find StashDB ID for performer: {performer.name}")
            return results
        
        # Get ALL scenes for this performer from StashDB - comprehensive approach
        try:
            max_pages = 5  # Reduced to prevent timeout - get up to 250 scenes per run
            all_scenes_processed = 0
            
            for page_num in range(1, max_pages + 1):
                try:
                    scenes_result = stashdb_api.get_performer_scenes(performer.stashdb_id, page=page_num)
                    scenes = scenes_result.get('scenes', [])
                    
                    if not scenes:
                        logger.info(f"No more scenes found for {performer.name} on page {page_num}")
                        break
                    
                    logger.info(f"Processing {len(scenes)} scenes for {performer.name} (page {page_num})")
                    
                    for scene_data in scenes:
                        try:
                            # Process each scene - this handles deduplication and filtering
                            scene_results = process_scene(scene_data, stash_api, config, performer_id=performer.id)
                            results['new_scenes'] += scene_results['new_scenes']
                            results['filtered_scenes'] += scene_results['filtered_scenes']
                            all_scenes_processed += 1
                        except Exception as e:
                            logger.error(f"Error processing scene for {performer.name}: {str(e)}")
                            continue
                    
                    # If we got fewer scenes than requested, we've reached the end
                    if len(scenes) < 50:
                        logger.info(f"Reached end of scenes for {performer.name} (got {len(scenes)} on page {page_num})")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching page {page_num} for performer {performer.name}: {str(e)}")
                    break
            
            logger.info(f"Processed {all_scenes_processed} total scenes for performer {performer.name}")
            
        except Exception as e:
            logger.warning(f"Could not fetch scenes for performer {performer.name}: {str(e)}")
            # Fallback: try search-based discovery
            try:
                performer_name = performer.name
                search_scenes = stashdb_api.search_scene(performer_name)
                logger.info(f"Fallback search found {len(search_scenes)} scenes for {performer.name}")
                
                for scene_data in search_scenes[:100]:  # Limit fallback to 100 scenes
                    try:
                        scene_results = process_scene(scene_data, stash_api, config, performer_id=performer.id)
                        results['new_scenes'] += scene_results['new_scenes']
                        results['filtered_scenes'] += scene_results['filtered_scenes']
                    except Exception as e:
                        logger.error(f"Error processing fallback scene: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Fallback search also failed for {performer.name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error processing performer {performer.name}: {str(e)}")
    
    return results

def process_studio_scenes(studio: Studio, stashdb_api: StashDBAPI, stash_api: StashAPI, config: Config) -> Dict:
    """Process ALL scenes for a specific studio, then filter locally"""
    logger.info(f"Getting ALL scenes for studio: {studio.name}")
    
    results = {'new_scenes': 0, 'filtered_scenes': 0}
    
    try:
        # Find studio in StashDB if not already linked
        if not studio.stashdb_id:
            stashdb_studios = stashdb_api.search_studio(studio.name)
            if stashdb_studios:
                # Try to match by name
                for ss in stashdb_studios:
                    if ss['name'].lower() == studio.name.lower():
                        studio.stashdb_id = ss['id']
                        break
        
        if not studio.stashdb_id:
            logger.warning(f"Could not find StashDB ID for studio: {studio.name}")
            return results
        
        # Get ALL scenes for this studio from StashDB - comprehensive approach
        try:
            max_pages = 10  # Reduced to prevent timeout - get up to 500 scenes per run
            all_scenes_processed = 0
            
            for page_num in range(1, max_pages + 1):
                try:
                    scenes_result = stashdb_api.get_studio_scenes(studio.stashdb_id, page=page_num)
                    scenes = scenes_result.get('scenes', [])
                    
                    if not scenes:
                        logger.info(f"No more scenes found for {studio.name} on page {page_num}")
                        break
                    
                    logger.info(f"Processing {len(scenes)} scenes for {studio.name} (page {page_num})")
                    
                    for scene_data in scenes:
                        try:
                            # Process each scene - this handles deduplication and filtering
                            scene_results = process_scene(scene_data, stash_api, config, studio_id=studio.id)
                            results['new_scenes'] += scene_results['new_scenes']
                            results['filtered_scenes'] += scene_results['filtered_scenes']
                            all_scenes_processed += 1
                        except Exception as e:
                            logger.error(f"Error processing scene for {studio.name}: {str(e)}")
                            continue
                    
                    # If we got fewer scenes than requested, we've reached the end
                    if len(scenes) < 50:
                        logger.info(f"Reached end of scenes for {studio.name} (got {len(scenes)} on page {page_num})")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching page {page_num} for studio {studio.name}: {str(e)}")
                    break
            
            logger.info(f"Processed {all_scenes_processed} total scenes for studio {studio.name}")
            
        except Exception as e:
            logger.warning(f"Could not fetch scenes for studio {studio.name}: {str(e)}")
            # Fallback: try search-based discovery
            try:
                studio_name = studio.name
                search_scenes = stashdb_api.search_scene(studio_name)
                logger.info(f"Fallback search found {len(search_scenes)} scenes for {studio.name}")
                
                # Filter scenes to only include those actually from this studio
                studio_scenes = []
                for scene in search_scenes:
                    scene_studio = scene.get('studio', {})
                    if scene_studio and scene_studio.get('name', '').lower() == studio_name.lower():
                        studio_scenes.append(scene)
                
                for scene_data in studio_scenes[:200]:  # Limit fallback to 200 scenes
                    try:
                        scene_results = process_scene(scene_data, stash_api, config, studio_id=studio.id)
                        results['new_scenes'] += scene_results['new_scenes']
                        results['filtered_scenes'] += scene_results['filtered_scenes']
                    except Exception as e:
                        logger.error(f"Error processing fallback scene: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Fallback search also failed for {studio.name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error processing studio {studio.name}: {str(e)}")
    
    return results

def process_scene(scene_data: Dict, stash_api: StashAPI, config: Config, performer_id: int = None, studio_id: int = None) -> Dict:
    """Process a single scene from StashDB with proper deduplication"""
    results = {'new_scenes': 0, 'filtered_scenes': 0}
    
    scene_id = scene_data.get('id')
    title = scene_data.get('title', 'Unknown Title')
    
    # Check if scene already exists in our database
    existing_scene = Scene.query.filter_by(stashdb_id=scene_id).first()
    
    if existing_scene:
        # Scene exists, but we might need to update associations
        updated = False
        
        # Update performer association if not already set
        if performer_id and not existing_scene.performer_id:
            existing_scene.performer_id = performer_id
            updated = True
            logger.debug(f"Added performer association to existing scene: {title}")
        
        # Update studio association if not already set
        if studio_id and not existing_scene.studio_id:
            existing_scene.studio_id = studio_id
            updated = True
            logger.debug(f"Added studio association to existing scene: {title}")
        
        # Update last_updated if we made changes
        if updated:
            existing_scene.last_updated = datetime.utcnow()
        
        return results  # Don't count as new scene
    
    # Check if scene exists in Stash (already owned)
    is_owned = stash_api.check_scene_exists(scene_id)
    
    # Apply filters
    is_filtered, filter_reason = apply_filters(scene_data, config)
    
    # Create new scene record
    scene = Scene(
        stashdb_id=scene_id,
        title=title,
        release_date=parse_date(scene_data.get('date')),
        duration=scene_data.get('duration'),
        performer_id=performer_id,
        studio_id=studio_id,
        is_owned=is_owned,
        is_filtered=is_filtered,
        filter_reason=filter_reason
    )
    
    # Set tags and categories
    tags = scene_data.get('tags', [])
    scene.set_tags([tag['name'] for tag in tags])
    scene.set_categories([tag['category'] for tag in tags if tag.get('category')])
    
    try:
        db.session.add(scene)
        db.session.flush()  # Get the scene.id before committing
        
        if is_filtered:
            results['filtered_scenes'] += 1
            logger.debug(f"Filtered scene: {title} - {filter_reason}")
            
            # Save filtered scene to database for exception management
            filtered_scene = FilteredScene(
                stash_id=None,  # We don't have stash_id, only stashdb_id
                stashdb_id=scene_id,
                title=title,
                studio=get_studio_name_from_scene(scene_data),
                duration=scene_data.get('duration'),
                release_date=scene_data.get('date'),
                filter_reason=filter_reason.split(':')[0] if ':' in filter_reason else 'category_filter',
                filter_category=filter_reason.split(':')[1].strip() if ':' in filter_reason else filter_reason,
                filter_details=filter_reason
            )
            
            # Set performers and tags
            performers = scene_data.get('performers', [])
            performer_names = [p.get('performer', {}).get('name', '') for p in performers]
            filtered_scene.set_performers(performer_names)
            
            tags = scene_data.get('tags', [])
            tag_names = [tag.get('name', '') for tag in tags]
            filtered_scene.set_tags(tag_names)
            
            db.session.add(filtered_scene)
            
        elif not is_owned:
            # Check if a WantedScene already exists for this StashDB ID
            existing_wanted = WantedScene.query.join(Scene).filter(
                Scene.stashdb_id == scene_id
            ).first()
            
            if not existing_wanted:
                # Add to wanted list if not filtered, not owned, and not already wanted
                wanted_scene = WantedScene(
                    scene_id=scene.id,
                    title=title,
                    performer_name=get_performer_name_from_scene(scene_data),
                    studio_name=get_studio_name_from_scene(scene_data),
                    release_date=scene.release_date,
                    status='wanted'
                )
                db.session.add(wanted_scene)
                scene.is_wanted = True
                results['new_scenes'] += 1
                logger.info(f"Added new wanted scene: {title}")
            else:
                logger.debug(f"Scene already in wanted list: {title}")
                scene.is_wanted = True
        
    except Exception as e:
        logger.error(f"Error adding scene {title}: {str(e)}")
        db.session.rollback()
        raise
    
    return results

def apply_filters(scene_data: Dict, config: Config) -> Tuple[bool, str]:
    """Apply category and duration filters to a scene"""
    
    # Get scene tags/categories
    tags = scene_data.get('tags', [])
    categories = [tag.get('category', '').lower() for tag in tags if tag.get('category')]
    tag_names = [tag.get('name', '').lower() for tag in tags]
    
    # Debug logging
    scene_title = scene_data.get('title', 'Unknown')
    unwanted_categories = [cat.lower() for cat in config.get_unwanted_categories()]
    
    logger.info(f"DEBUG - Scene: {scene_title}")
    logger.info(f"DEBUG - Tags from StashDB: {tag_names[:5]}...")  # First 5 tags
    logger.info(f"DEBUG - Categories from StashDB: {categories}")
    logger.info(f"DEBUG - Unwanted categories configured: {unwanted_categories}")
    
    # Check unwanted categories
    for unwanted in unwanted_categories:
        if unwanted in categories or unwanted in tag_names:
            logger.info(f"FILTERED - Scene '{scene_title}' contains unwanted category/tag: {unwanted}")
            return True, f"Contains unwanted category: {unwanted}"
    
    # Check required categories
    required_categories = [cat.lower() for cat in config.get_required_categories()]
    if required_categories:
        has_required = False
        for required in required_categories:
            if required in categories or required in tag_names:
                has_required = True
                break
        
        if not has_required:
            return True, f"Missing required categories: {', '.join(required_categories)}"
    
    # Check duration filters
    duration = scene_data.get('duration')
    if duration:
        duration_minutes = duration / 60
        
        if config.min_duration_minutes > 0 and duration_minutes < config.min_duration_minutes:
            return True, f"Duration too short: {duration_minutes:.1f} min < {config.min_duration_minutes} min"
        
        if config.max_duration_minutes > 0 and duration_minutes > config.max_duration_minutes:
            return True, f"Duration too long: {duration_minutes:.1f} min > {config.max_duration_minutes} min"
    
    logger.info(f"PASSED - Scene '{scene_title}' passed all filters")
    return False, ""

def add_wanted_scenes_to_whisparr(whisparr_api: WhisparrAPI, config: Config) -> Dict:
    """Add wanted scenes to Whisparr using StashDB UUID lookup"""
    results = {'added_count': 0, 'errors': [], 'skipped_count': 0}
    
    # Get scenes that need to be added to Whisparr
    wanted_scenes = WantedScene.query.filter_by(
        added_to_whisparr=False,
        status='wanted'
    ).limit(50).all()  # Limit to prevent overwhelming Whisparr
    
    logger.info(f"Processing {len(wanted_scenes)} wanted scenes for Whisparr addition")
    
    for wanted in wanted_scenes:
        try:
            # Get the scene's StashDB UUID
            scene = wanted.scene
            if not scene or not scene.stashdb_id:
                logger.warning(f"No StashDB ID found for scene: {wanted.title}")
                results['errors'].append(f"No StashDB ID for {wanted.title}")
                continue
            
            stashdb_uuid = scene.stashdb_id
            logger.info(f"Processing scene: {wanted.title} (StashDB: {stashdb_uuid})")
            
            # Check if scene already exists in Whisparr by UUID
            if whisparr_api.check_scene_exists_by_uuid(stashdb_uuid):
                logger.info(f"Scene already exists in Whisparr: {wanted.title}")
                wanted.added_to_whisparr = True
                wanted.status = 'exists'
                results['skipped_count'] += 1
                continue
            
            # Add scene to Whisparr using UUID-based method
            logger.info(f"Adding scene to Whisparr via UUID: {wanted.title}")
            result = whisparr_api.add_scene_by_uuid(
                stashdb_uuid=stashdb_uuid,
                quality_profile_id=config.whisparr_quality_profile_id if hasattr(config, 'whisparr_quality_profile_id') else None,
                root_folder_path='/data/media/y'  # From your config
            )
            
            if result:
                wanted.added_to_whisparr = True
                wanted.whisparr_id = str(result.get('id', ''))
                wanted.status = 'requested'
                results['added_count'] += 1
                logger.info(f"Successfully added scene to Whisparr: {wanted.title} (Whisparr ID: {result.get('id')})")
            else:
                error_msg = f"Failed to add {wanted.title} to Whisparr - no result returned"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                
        except Exception as e:
            error_msg = f"Error adding {wanted.title} to Whisparr: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
    
    logger.info(f"Whisparr addition completed: {results['added_count']} added, {results['skipped_count']} skipped, {len(results['errors'])} errors")
    return results

def get_performer_name_from_scene(scene_data: Dict) -> str:
    """Extract main performer name from scene data"""
    performers = scene_data.get('performers', [])
    if performers:
        return performers[0].get('performer', {}).get('name', '')
    return ''

def get_studio_name_from_scene(scene_data: Dict) -> str:
    """Extract studio name from scene data"""
    studio = scene_data.get('studio', {})
    return studio.get('name', '') if studio else ''

def cleanup_duplicate_scenes() -> Dict:
    """Remove duplicate scenes and wanted scenes"""
    logger.info("Starting duplicate scene cleanup")
    
    results = {
        'status': 'success',
        'removed_scenes': 0,
        'removed_wanted': 0,
        'updated_scenes': 0,
        'errors': []
    }
    
    try:
        # Find duplicate scenes (same stashdb_id)
        duplicate_groups = db.session.query(
            Scene.stashdb_id,
            db.func.count(Scene.id).label('count')
        ).group_by(Scene.stashdb_id).having(db.func.count(Scene.id) > 1).all()
        
        for stashdb_id, count in duplicate_groups:
            # Get all scenes with this stashdb_id
            duplicate_scenes = Scene.query.filter_by(stashdb_id=stashdb_id).order_by(Scene.discovered_date.asc()).all()
            
            if len(duplicate_scenes) > 1:
                # Keep the first scene (oldest), merge data into it
                primary_scene = duplicate_scenes[0]
                
                for duplicate in duplicate_scenes[1:]:
                    try:
                        # Merge performer and studio associations
                        if not primary_scene.performer_id and duplicate.performer_id:
                            primary_scene.performer_id = duplicate.performer_id
                        
                        if not primary_scene.studio_id and duplicate.studio_id:
                            primary_scene.studio_id = duplicate.studio_id
                        
                        # Update wanted scenes to point to primary scene
                        wanted_scenes = WantedScene.query.filter_by(scene_id=duplicate.id).all()
                        for wanted in wanted_scenes:
                            # Check if primary scene already has a wanted entry
                            existing_wanted = WantedScene.query.filter_by(scene_id=primary_scene.id).first()
                            if not existing_wanted:
                                wanted.scene_id = primary_scene.id
                            else:
                                db.session.delete(wanted)
                                results['removed_wanted'] += 1
                        
                        # Delete the duplicate scene
                        db.session.delete(duplicate)
                        results['removed_scenes'] += 1
                        logger.info(f"Removed duplicate scene: {duplicate.title}")
                        
                    except Exception as e:
                        logger.error(f"Error processing duplicate scene {duplicate.title}: {str(e)}")
                        results['errors'].append(f"Error processing duplicate {duplicate.title}: {str(e)}")
                
                # Update the primary scene
                primary_scene.last_updated = datetime.utcnow()
                results['updated_scenes'] += 1
        
        # Find and remove duplicate wanted scenes (same scene_id)
        duplicate_wanted_groups = db.session.query(
            WantedScene.scene_id,
            db.func.count(WantedScene.id).label('count')
        ).group_by(WantedScene.scene_id).having(db.func.count(WantedScene.id) > 1).all()
        
        for scene_id, count in duplicate_wanted_groups:
            duplicate_wanted = WantedScene.query.filter_by(scene_id=scene_id).order_by(WantedScene.added_date.asc()).all()
            
            if len(duplicate_wanted) > 1:
                # Keep the first wanted entry, remove the rest
                for wanted in duplicate_wanted[1:]:
                    db.session.delete(wanted)
                    results['removed_wanted'] += 1
                    logger.info(f"Removed duplicate wanted scene: {wanted.title}")
        
        db.session.commit()
        
        logger.info(f"Cleanup completed: {results['removed_scenes']} scenes, {results['removed_wanted']} wanted scenes removed")
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Cleanup failed: {str(e)}"
        logger.error(error_msg)
        results['status'] = 'error'
        results['errors'].append(error_msg)
    
    return results

def parse_date(date_str: str):
    """Parse date string to date object"""
    if not date_str:
        return None
    
    try:
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
    
    return None
# COMPREHENSIVE APPROACH - Rebuild timestamp: 1755856261
