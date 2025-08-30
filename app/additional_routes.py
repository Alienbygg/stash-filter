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
            
            if not scene_title:
                return jsonify({'error': 'Scene title is required'}), 400
            
            # For now, return success to remove the placeholder message
            return jsonify({
                'success': True,
                'message': f'Scene "{scene_title}" would be added to Whisparr (feature in development)'
            })
            
        except Exception as e:
            logger.error(f"Error in add_scene_to_whisparr: {str(e)}")
            return jsonify({'error': str(e)}), 500
