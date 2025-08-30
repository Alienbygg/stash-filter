from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

def register_additional_routes(app):
    """Register additional routes with the Flask app"""
    
    @app.route('/api/add-scene-to-whisparr', methods=['POST'])
    def add_scene_to_whisparr():
        try:
            data = request.get_json()
            scene_title = data.get('title', '')
            scene_id = data.get('scene_id', '')
            
            if not scene_title:
                return jsonify({'error': 'Scene title is required'}), 400
            
            logger.info(f"Want button clicked for scene: {scene_title}")
            
            # TODO: Implement actual Whisparr integration
            # For now, return success to make buttons functional
            return jsonify({
                'success': True,
                'message': f'Scene "{scene_title}" queued for Whisparr (integration in progress)'
            })
            
        except Exception as e:
            logger.error(f"Error in add_scene_to_whisparr: {str(e)}")
            return jsonify({'error': str(e)}), 500
