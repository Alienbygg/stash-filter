def add_trending_performer_safe(performer_data):
    """Safely add trending performer with nullable stash_id"""
    try:
        from app.models import db, Performer
        
        # Check if performer already exists
        existing = Performer.query.filter_by(name=performer_data.get('name')).first()
        if existing:
            return existing
        
        # Create new performer with nullable stash_id
        new_performer = Performer(
            name=performer_data.get('name'),
            stashdb_id=performer_data.get('id'),
            stash_id=None,  # Allow null for trending performers
            aliases=performer_data.get('aliases', ''),
            monitored=False
        )
        
        db.session.add(new_performer)
        db.session.commit()
        return new_performer
        
    except Exception as e:
        logger.error(f"Error adding trending performer: {str(e)}")
        db.session.rollback()
        return None
