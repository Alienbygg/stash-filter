import logging
from app.models import db, Performer
from app.stashdb_api import StashDBAPI

logger = logging.getLogger(__name__)

def fetch_missing_stashdb_ids():
    """Fetch missing StashDB IDs for monitored performers"""
    try:
        stashdb = StashDBAPI()
        
        # Find performers without StashDB ID
        performers_missing_ids = Performer.query.filter(
            Performer.monitored == True,
            Performer.stashdb_id.is_(None)
        ).all()
        
        logger.info(f"Found {len(performers_missing_ids)} performers missing StashDB IDs")
        
        updated_count = 0
        for performer in performers_missing_ids:
            try:
                results = stashdb.search_performer(performer.name)
                if results and len(results) > 0:
                    performer.stashdb_id = results[0].get('id')
                    logger.info(f"Found StashDB ID {performer.stashdb_id} for {performer.name}")
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Error searching StashDB for {performer.name}: {str(e)}")
                continue
        
        db.session.commit()
        return updated_count
        
    except Exception as e:
        logger.error(f"Error in fetch_missing_stashdb_ids: {str(e)}")
        db.session.rollback()
        return 0
