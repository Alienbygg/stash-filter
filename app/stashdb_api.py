import requests
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StashDBAPI:
    """API client for StashDB"""
    
    def __init__(self):
        self.base_url = os.environ.get('STASHDB_URL', 'https://stashdb.org')
        self.api_key = os.environ.get('STASHDB_API_KEY')
        self.graphql_endpoint = f"{self.base_url}/graphql"
        
        self.headers = {
            'Content-Type': 'application/json',
            'ApiKey': self.api_key
        }
    
    def _make_request(self, query: str, variables: Dict = None) -> Dict:
        """Make a GraphQL request to StashDB"""
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = requests.post(
                self.graphql_endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Log the response for debugging
            logger.debug(f"StashDB API Response Status: {response.status_code}")
            logger.debug(f"StashDB API Response: {response.text[:500]}...")
            
            response.raise_for_status()
            
            result = response.json()
            if 'errors' in result:
                error_msg = f"StashDB GraphQL errors: {result['errors']}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return result.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"StashDB API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"StashDB Response content: {e.response.text[:500]}")
            raise Exception(f"Failed to connect to StashDB: {str(e)}")
    
    def search_performer(self, name: str) -> List[Dict]:
        """Search for performer by name in StashDB"""
        query = '''
        query SearchPerformer($term: String!) {
            searchPerformer(term: $term) {
                id
                name
            }
        }
        '''
        
        variables = {'term': name}
        
        try:
            data = self._make_request(query, variables)
            results = data.get('searchPerformer', [])
            logger.info(f"Found {len(results)} results for performer: {name}")
            return results
        except Exception as e:
            logger.error(f"Error searching performer: {str(e)}")
            return self._search_performer_fallback(name)
    
    def search_studio(self, name: str) -> List[Dict]:
        """Search for studio by name in StashDB"""
        query = '''
        query SearchStudio($term: String!) {
            searchStudio(term: $term) {
                id
                name
            }
        }
        '''
        
        variables = {'term': name}
        
        try:
            data = self._make_request(query, variables)
            results = data.get('searchStudio', [])
            logger.info(f"Found {len(results)} results for studio: {name}")
            return results
        except Exception as e:
            logger.error(f"Error searching studio: {str(e)}")
            return self._search_studio_fallback(name)
    
    def _search_performer_fallback(self, name: str) -> List[Dict]:
        """Fallback method for performer search"""
        logger.warning(f"Using fallback for performer search: {name}")
        return []
    
    def search_scene(self, title: str, year: int = None) -> List[Dict]:
        """Search for scene by title in StashDB"""
        query = '''
        query SearchScene($term: String!) {
            searchScene(term: $term) {
                id
                title
                date
                duration
                studio {
                    id
                    name
                }
                performers {
                    performer {
                        id
                        name
                    }
                }
            }
        }
        '''
        
        variables = {'term': title}
        
        try:
            data = self._make_request(query, variables)
            results = data.get('searchScene', [])
            
            # Filter by year if provided
            if year and results:
                filtered_results = []
                for scene in results:
                    scene_date = scene.get('date', '')
                    if scene_date and str(year) in scene_date:
                        filtered_results.append(scene)
                results = filtered_results
            
            logger.info(f"Found {len(results)} results for scene: {title}")
            return results
        except Exception as e:
            logger.error(f"Error searching scene: {str(e)}")
            return []
    
    def _search_studio_fallback(self, name: str) -> List[Dict]:
        """Fallback method for studio search"""
        logger.warning(f"Using fallback for studio search: {name}")
        return []
    
    def _get_performer_scenes_fallback(self, performer_id: str) -> Dict:
        """Fallback method for performer scenes when GraphQL queries fail"""
        try:
            # First get performer details
            query = '''
            query GetPerformerDetails($id: ID!) {
                findPerformer(id: $id) {
                    id
                    name
                }
            }
            '''
            
            variables = {'id': performer_id}
            data = self._make_request(query, variables)
            performer_data = data.get('findPerformer', {})
            
            if performer_data and performer_data.get('name'):
                # Search for scenes featuring this performer by name
                performer_name = performer_data['name']
                scenes = self.search_scene(performer_name)
                
                # Filter to scenes that actually feature this performer
                filtered_scenes = []
                for scene in scenes:
                    scene_performers = scene.get('performers', [])
                    for perf in scene_performers:
                        perf_data = perf.get('performer', {})
                        if perf_data.get('name', '').lower() == performer_name.lower():
                            filtered_scenes.append(scene)
                            break
                
                logger.info(f"Fallback found {len(filtered_scenes)} scenes for performer {performer_name}")
                return {'count': len(filtered_scenes), 'scenes': filtered_scenes}
            else:
                logger.warning(f"Could not find performer details for ID: {performer_id}")
                return {'count': 0, 'scenes': []}
                
        except Exception as e:
            logger.error(f"Fallback error getting performer scenes: {str(e)}")
            return {'count': 0, 'scenes': []}
    
    def _get_studio_scenes_fallback(self, studio_id: str) -> Dict:
        """Fallback method for studio scenes when GraphQL queries fail"""
        try:
            # First get studio details
            query = '''
            query GetStudioDetails($id: ID!) {
                findStudio(id: $id) {
                    id
                    name
                }
            }
            '''
            
            variables = {'id': studio_id}
            data = self._make_request(query, variables)
            studio_data = data.get('findStudio', {})
            
            if studio_data and studio_data.get('name'):
                # Search for scenes from this studio by name
                studio_name = studio_data['name']
                scenes = self.search_scene(studio_name)
                
                # Filter scenes to only include those actually from this studio
                studio_scenes = []
                for scene in scenes:
                    scene_studio = scene.get('studio', {})
                    if scene_studio and scene_studio.get('name', '').lower() == studio_name.lower():
                        studio_scenes.append(scene)
                
                logger.info(f"Fallback found {len(studio_scenes)} scenes for studio {studio_name}")
                return {'count': len(studio_scenes), 'scenes': studio_scenes}
            else:
                logger.warning(f"Could not find studio details for ID: {studio_id}")
                return {'count': 0, 'scenes': []}
                
        except Exception as e:
            logger.error(f"Fallback error getting studio scenes: {str(e)}")
            return {'count': 0, 'scenes': []}
    
    def get_performer_scenes(self, performer_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get scenes for a specific performer from StashDB using correct queryScenes schema"""
        query = '''
        query GetPerformerScenes($input: SceneQueryInput!) {
            queryScenes(input: $input) {
                count
                scenes {
                    id
                    title
                    date
                    duration
                    director
                    studio {
                        id
                        name
                    }
                    performers {
                        performer {
                            id
                            name
                        }
                    }
                    tags {
                        id
                        name
                    }
                    images {
                        url
                        width
                        height
                    }
                    urls {
                        url
                        type
                    }
                }
            }
        }
        '''
        
        variables = {
            'input': {
                'page': page,
                'per_page': limit,
                'performers': [performer_id],
                'sort': 'DATE',
                'direction': 'DESC'
            }
        }
        
        try:
            data = self._make_request(query, variables)
            query_result = data.get('queryScenes', {})
            scenes = query_result.get('scenes', [])
            count = query_result.get('count', 0)
            
            logger.info(f"Found {len(scenes)} scenes for performer ID {performer_id} (total: {count})")
            return {'count': count, 'scenes': scenes}
            
        except Exception as e:
            logger.error(f"Error getting performer scenes: {str(e)}")
            # Fallback to search-based method
            return self._get_performer_scenes_fallback(performer_id)
    
    def get_studio_scenes(self, studio_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get scenes for a specific studio from StashDB using correct queryScenes schema"""
        query = '''
        query GetStudioScenes($input: SceneQueryInput!) {
            queryScenes(input: $input) {
                count
                scenes {
                    id
                    title
                    date
                    duration
                    director
                    studio {
                        id
                        name
                    }
                    performers {
                        performer {
                            id
                            name
                        }
                    }
                    tags {
                        id
                        name
                    }
                    images {
                        url
                        width
                        height
                    }
                    urls {
                        url
                        type
                    }
                }
            }
        }
        '''
        
        variables = {
            'input': {
                'page': page,
                'per_page': limit,
                'parentStudio': studio_id,
                'sort': 'DATE',
                'direction': 'DESC'
            }
        }
        
        try:
            data = self._make_request(query, variables)
            query_result = data.get('queryScenes', {})
            scenes = query_result.get('scenes', [])
            count = query_result.get('count', 0)
            
            logger.info(f"Found {len(scenes)} scenes for studio ID {studio_id} (total: {count})")
            return {'count': count, 'scenes': scenes}
            
        except Exception as e:
            logger.error(f"Error getting studio scenes: {str(e)}")
            # Fallback to search-based method
            return self._get_studio_scenes_fallback(studio_id)
    
    def get_recent_scenes(self, days: int = 7, page: int = 1) -> Dict:
        """Get recently added scenes from StashDB"""
        # Since we can't query by date, search for some popular terms
        # This is a workaround until we find the correct schema
        search_terms = ["new", "latest", "2025", "recent"]
        all_scenes = []
        
        for term in search_terms:
            try:
                scenes = self.search_scene(term)
                all_scenes.extend(scenes)
            except Exception as e:
                logger.error(f"Error searching for recent scenes with term '{term}': {str(e)}")
                continue
        
        # Remove duplicates based on scene ID
        unique_scenes = []
        seen_ids = set()
        for scene in all_scenes:
            scene_id = scene.get('id')
            if scene_id and scene_id not in seen_ids:
                unique_scenes.append(scene)
                seen_ids.add(scene_id)
        
        logger.info(f"Found {len(unique_scenes)} recent scenes")
        return {'count': len(unique_scenes), 'scenes': unique_scenes}
    
    def get_scene_details(self, scene_id: str) -> Optional[Dict]:
        """Get detailed information about a specific scene"""
        query = '''
        query GetScene($id: ID!) {
            findScene(id: $id) {
                id
                title
                date
                duration
                director
                code
                details
                studio {
                    id
                    name
                }
                performers {
                    performer {
                        id
                        name
                    }
                }
                tags {
                    id
                    name
                    description
                }
                images {
                    url
                    width
                    height
                }
                urls {
                    url
                    type
                }
            }
        }
        '''
        
        variables = {'id': scene_id}
        
        try:
            data = self._make_request(query, variables)
            return data.get('findScene')
        except Exception as e:
            logger.error(f"Error getting scene details: {str(e)}")
            return None
    
    def get_all_tags(self, limit: int = 100) -> List[Dict]:
        """Get all available tags from StashDB for category filtering using pagination"""
        all_tags = []
        page = 1
        total_count = None
        
        while True:
            query = '''
            query GetAllTags($input: TagQueryInput!) {
                queryTags(input: $input) {
                    count
                    tags {
                        id
                        name
                        description
                        category {
                            id
                            name
                            description
                        }
                    }
                }
            }
            '''
            
            variables = {
                'input': {
                    'page': page,
                    'per_page': limit,
                    'sort': 'NAME',
                    'direction': 'ASC'
                }
            }
            
            try:
                data = self._make_request(query, variables)
                query_result = data.get('queryTags', {})
                tags = query_result.get('tags', [])
                count = query_result.get('count', 0)
                
                # Set total count from first request
                if total_count is None:
                    total_count = count
                    logger.info(f"Found {total_count} total tags in StashDB, fetching in batches of {limit}")
                
                if not tags:
                    break
                    
                all_tags.extend(tags)
                logger.info(f"Retrieved page {page}: {len(tags)} tags (total so far: {len(all_tags)})")
                
                # Check if we've got all tags
                if len(all_tags) >= total_count or len(tags) < limit:
                    break
                    
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 50:  # Max 50 pages = 5000 tags
                    logger.warning(f"Reached maximum page limit, stopping pagination")
                    break
                    
            except Exception as e:
                logger.error(f"Error getting tags from StashDB page {page}: {str(e)}")
                break
        
        logger.info(f"Retrieved {len(all_tags)} tags from StashDB (total available: {total_count})")
        return all_tags
    
    def test_connection(self) -> bool:
        """Test connection to StashDB using a working query"""
        query = '''
        query TestConnection {
            queryTags(input: {page: 1, per_page: 1}) {
                count
            }
        }
        '''
        
        try:
            data = self._make_request(query)
            # If we can query tags, the connection works
            tag_data = data.get('queryTags', {})
            count = tag_data.get('count', 0)
            logger.info(f"StashDB connection test successful - {count} tags available")
            return True
        except Exception as e:
            logger.error(f"StashDB connection test failed: {str(e)}")
            return False

# Enhanced StashDB Discovery - Fixed Import Issue
# Enhanced GraphQL queries with fallback methods
# Rebuild timestamp: 1724279624
# Fixed StashDB Import Issue - Rebuild timestamp: 1755847602
# FIXED: StashDB GraphQL Schema - Rebuild timestamp: 1755848417
# FIXED: StashDB GraphQL Schema - Rebuild timestamp: 1755850355
# FINAL SCHEMA FIX - Rebuild timestamp: 1755851489
