# Date filtering logic to integrate into wanted_scenes route in main.py:

from datetime import datetime

@app.route('/wanted_scenes')  
def wanted_scenes():
    # Get date parameters
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    
    # Build filtered query
    query = WantedScene.query
    
    if from_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            query = query.filter(WantedScene.release_date >= from_date)
        except ValueError:
            pass  # Invalid date format
    
    if to_date_str:
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() 
            query = query.filter(WantedScene.release_date <= to_date)
        except ValueError:
            pass  # Invalid date format
    
    # Always sort by release_date descending (newest first)
    wanted_scenes = query.order_by(WantedScene.release_date.desc()).all()
    
    return render_template('wanted_scenes.html', 
                         wanted_scenes=wanted_scenes,
                         from_date_str=from_date_str,
                         to_date_str=to_date_str)
