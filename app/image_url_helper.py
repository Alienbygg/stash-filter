import os

def fix_image_url(image_path):
    """Simple helper to fix scene image URLs"""
    if not image_path:
        return '/static/images/scene-placeholder.jpg'
    
    stash_url = os.environ.get('STASH_URL', 'http://localhost:6969').rstrip('/')
    
    if image_path.startswith('http'):
        return image_path
    elif image_path.startswith('/'):
        return stash_url + image_path
    else:
        return stash_url + '/' + image_path
