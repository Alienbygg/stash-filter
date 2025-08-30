@app.route('/wanted_scenes')
def wanted_scenes():
    """Wanted scenes page with date filtering"""
    from datetime import datetime, timedelta
    
    # Get date parameters from request
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')
    
    from_date = None
    to_date = None
    
    if from_date_str:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    if to_date_str:
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    # If no dates provided, default to last year
    if not from_date and not to_date:
        to_date = datetime.now().date()
        from_date = to_date - timedelta(days=365)
    
    # Get filtered and sorted scenes
    wanted_scenes = get_wanted_scenes_with_date_filter(from_date, to_date)
    
    return render_template('wanted_scenes.html', 
                         wanted_scenes=wanted_scenes,
                         from_date=from_date,
                         to_date=to_date)
