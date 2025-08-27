import requests
import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class StashAPI:
    """API client for Stash"""
    
    def __init__(self):
        self.base_url = os.environ.get('STASH_URL', 'http://10.11.12.70:6969')
        self.api_key = os.environ.get('STASH_API_KEY')
        self.graphql_endpoint = f"{self.base_url}/graphql"
        
        self.headers = {
            'Content-Type': 'application/json',
            'ApiKey': self.api_key
        }
    
    def _make_request(self, query: str, variables: Dict = None) -> Dict:
        """Make a GraphQL request to Stash"""
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
            logger.debug(f"Stash API Response Status: {response.status_code}")
            logger.debug(f"Stash API Response: {response.text[:500]}...")
            
            response.raise_for_status()
            
            result = response.json()
            if 'errors' in result:
                error_msg = f"Stash GraphQL errors: {result['errors']}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            return result.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Stash API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text[:500]}")
            raise Exception(f"Failed to connect to Stash: {str(e)}")
    
    def get_favorites(self) -> Dict[str, List]:
        """Get favorite performers and studios from Stash using pagination"""
        all_favorites = {'performers': [], 'studios': []}
        
        # Get all favorite performers with pagination
        performers = self._get_all_favorites_paginated('performers')
        studios = self._get_all_favorites_paginated('studios')
        
        logger.info(f"Total sync results: {len(performers)} favorite performers, {len(studios)} favorite studios")
        
        return {
            'performers': performers,
            'studios': studios
        }
    
    def _get_all_favorites_paginated(self, entity_type: str) -> List[Dict]:
        """Get all favorites of a specific type using pagination"""
        all_favorites = []
        page = 1
        per_page = 100
        
        while True:
            if entity_type == 'performers':
                query = '''
                query GetPerformers($page: Int!, $per_page: Int!) {
                    findPerformers(filter: { page: $page, per_page: $per_page }) {
                        count
                        performers {
                            id
                            name
                            favorite
                        }
                    }
                }
                '''
            else:  # studios
                query = '''
                query GetStudios($page: Int!, $per_page: Int!) {
                    findStudios(filter: { page: $page, per_page: $per_page }) {
                        count
                        studios {
                            id
                            name
                            favorite
                        }
                    }
                }
                '''
            
            try:
                variables = {'page': page, 'per_page': per_page}
                data = self._make_request(query, variables)
                
                if entity_type == 'performers':
                    items = data.get('findPerformers', {}).get('performers', [])
                    total_count = data.get('findPerformers', {}).get('count', 0)
                else:
                    items = data.get('findStudios', {}).get('studios', [])
                    total_count = data.get('findStudios', {}).get('count', 0)
                
                # Filter only favorites
                favorites_on_page = [item for item in items if item.get('favorite', False)]
                all_favorites.extend(favorites_on_page)
                
                logger.info(f"Page {page} for {entity_type}: {len(favorites_on_page)} favorites out of {len(items)} items")
                
                # Check if we've got all pages
                if len(items) < per_page or (page * per_page) >= total_count:
                    break
                    
                page += 1
                
            except Exception as e:
                logger.error(f"Error getting {entity_type} page {page}: {str(e)}")
                break
        
        logger.info(f"Found {len(all_favorites)} total favorite {entity_type}")
        return all_favorites
    
    def _get_favorites_fallback(self) -> Dict[str, List]:
        """Fallback method for getting favorites with minimal GraphQL"""
        try:
            # Try the absolute simplest query possible
            query = '''
            query SystemStatus {
                systemStatus {
                    databaseSchema
                }
            }
            '''
            
            self._make_request(query)
            logger.warning("Basic connection works, but favorites query is incompatible. Returning empty results.")
            
            return {
                'performers': [],
                'studios': []
            }
            
        except Exception as e:
            logger.error(f"Even fallback query failed: {str(e)}")
            return {
                'performers': [],
                'studios': []
            }
    
    def get_scenes(self, page: int = 1, per_page: int = 25) -> Dict:
        """Get scenes from Stash"""
        query = '''
        query FindScenes($filter: FindFilterType!) {
            findScenes(filter: $filter) {
                count
                scenes {
                    id
                    title
                    date
                    rating100
                    performers {
                        id
                        name
                    }
                    studio {
                        id
                        name
                    }
                    tags {
                        id
                        name
                    }
                    stash_ids {
                        stash_id
                        endpoint
                    }
                    files {
                        duration
                        path
                    }
                }
            }
        }
        '''
        
        variables = {
            'filter': {
                'page': page,
                'per_page': per_page,
                'sort': 'created_at',
                'direction': 'DESC'
            }
        }
        
        data = self._make_request(query, variables)
        return data.get('findScenes', {})
    
    def check_scene_exists(self, stashdb_id: str) -> bool:
        """Check if a scene with given StashDB ID exists in Stash"""
        # Temporarily disabled due to GraphQL compatibility issues with Stash v0.28.1
        # TODO: Fix GraphQL query for proper Stash version compatibility
        logger.warning(f"Scene existence check disabled for StashDB ID: {stashdb_id}")
        return False  # Assume scene doesn't exist to avoid errors
    
    def get_performer_scenes(self, performer_id: str) -> List[Dict]:
        """Get scenes for a specific performer"""
        query = '''
        query GetPerformerScenes($id: ID!) {
            findPerformer(id: $id) {
                scene_count
                scenes {
                    id
                    title
                    date
                    stash_ids {
                        stash_id
                        endpoint
                    }
                }
            }
        }
        '''
        
        variables = {'id': performer_id}
        
        try:
            data = self._make_request(query, variables)
            performer_data = data.get('findPerformer', {})
            return performer_data.get('scenes', [])
        except Exception as e:
            logger.error(f"Error getting performer scenes: {str(e)}")
            return []
    
    def get_studio_scenes(self, studio_id: str) -> List[Dict]:
        """Get scenes for a specific studio"""
        query = '''
        query GetStudioScenes($id: ID!) {
            findStudio(id: $id) {
                scene_count
                scenes {
                    id
                    title
                    date
                    stash_ids {
                        stash_id
                        endpoint
                    }
                }
            }
        }
        '''
        
        variables = {'id': studio_id}
        
        try:
            data = self._make_request(query, variables)
            studio_data = data.get('findStudio', {})
            return studio_data.get('scenes', [])
        except Exception as e:
            logger.error(f"Error getting studio scenes: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """Test connection to Stash"""
        query = '''
        query SystemStatus {
            systemStatus {
                databaseSchema
                databasePath
                appSchema
            }
        }
        '''
        
        try:
            self._make_request(query)
            logger.info("Stash connection test successful")
            return True
        except Exception as e:
            logger.error(f"Stash connection test failed: {str(e)}")
            return False
