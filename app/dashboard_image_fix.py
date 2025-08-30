def fix_scene_image_url(scene):
    """Fix scene image URL to include Stash server base"""
    stash_url = os.environ.get('STASH_URL', 'http://localhost:6969').rstrip('/')
    
    if 'screenshot' in scene and scene['screenshot']:
        if scene['screenshot'].startswith('/'):
            scene['image'] = stash_url + scene['screenshot']
        elif not scene['screenshot'].startswith('http'):
            scene['image'] = stash_url + '/' + scene['screenshot']
        else:
            scene['image'] = scene['screenshot']
    elif 'image' in scene and scene['image']:
        if scene['image'].startswith('/'):
            scene['image'] = stash_url + scene['image']
        elif not scene['image'].startswith('http'):
            scene['image'] = stash_url + '/' + scene['image']
    else:
        scene['image'] = '/static/images/scene-placeholder.jpg'
    
    return scene
