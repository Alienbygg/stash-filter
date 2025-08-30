# This should be integrated into the existing wanted_scenes route in main.py
# Find the WantedScene.query and modify it to:
wanted_scenes = WantedScene.query.order_by(WantedScene.release_date.desc()).all()
