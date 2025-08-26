import requests
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WhisparrAPI:
    """API client for Whisparr"""
    
    def __init__(self):
        self.base_url = os.environ.get('WHISPARR_URL', 'http://10.11.12.77:6969')
        self.api_key = os.environ.get('WHISPARR_API_KEY')
        
        self.headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': self.api_key
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make an API request to Whisparr"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        
        # For scene endpoint, use URL parameters like the working bash script
        if 'scene' in endpoint:
            params = {'apikey': self.api_key}
            headers = {'Content-Type': 'application/json'}
        else:
            params = None
            headers = self.headers
        
        try:
            if method.upper() == 'GET':
                # Always use URL params for GET requests
                response = requests.get(url, headers={'Content-Type': 'application/json'}, 
                                      params={'apikey': self.api_key}, timeout=30)
            elif method.upper() == 'POST':
                logger.info(f"Whisparr POST request to {url} with data: {json.dumps(data, indent=2) if data else 'None'}")
                if params:
                    # Use URL params for scene endpoint (like bash script)
                    response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
                else:
                    # Use headers for other endpoints
                    response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Whisparr API request failed: {str(e)}")
            # Log the response content if available for debugging
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_content = e.response.text
                    logger.error(f"Whisparr error response: {error_content}")
                except:
                    logger.error("Could not decode Whisparr error response")
            raise Exception(f"Failed to connect to Whisparr: {str(e)}")
    
    def get_movies(self) -> List[Dict]:
        """Get all movies from Whisparr"""
        try:
            return self._make_request('GET', 'movie')
        except Exception as e:
            logger.error(f"Error getting movies: {str(e)}")
            return []
    
    def search_movie(self, title: str, year: int = None) -> List[Dict]:
        """Search for a movie by title"""
        try:
            endpoint = f"movie/lookup?term={requests.utils.quote(title)}"
            if year:
                endpoint += f"&year={year}"
            
            return self._make_request('GET', endpoint)
        except Exception as e:
            logger.error(f"Error searching movie: {str(e)}")
            return []
    
    def add_movie(self, movie_data: Dict) -> Optional[Dict]:
        """Add a movie to Whisparr with StashDB validation"""
        required_fields = {
            'title': movie_data.get('title'),
            'qualityProfileId': movie_data.get('qualityProfileId', self._get_quality_profile_id()),
            'monitored': movie_data.get('monitored', True),
            'minimumAvailability': movie_data.get('minimumAvailability', 'released'),
            'rootFolderPath': movie_data.get('rootFolderPath', '/data/media/y'),
            'addOptions': movie_data.get('addOptions', {'searchForMovie': True})
        }
        
        # Handle different movie sources
        if 'tmdbId' in movie_data:
            required_fields['tmdbId'] = movie_data['tmdbId']
        elif 'imdbId' in movie_data:
            required_fields['imdbId'] = movie_data['imdbId']
        elif 'movieFile' in movie_data:
            required_fields['movieFile'] = movie_data['movieFile']
        
        # Add optional fields
        optional_fields = ['year', 'studio', 'overview', 'images', 'genres', 'ratings']
        for field in optional_fields:
            if field in movie_data:
                required_fields[field] = movie_data[field]
        
        # Add dummy external ID to satisfy Whisparr's requirements
        # Since adult scenes don't have TMDB/IMDB IDs, we use a fake one
        if 'tmdbId' not in movie_data and 'imdbId' not in movie_data:
            # Use a hash of the title as a fake TMDB ID to make it unique
            import hashlib
            title_hash = hashlib.md5(movie_data.get('title', '').encode()).hexdigest()
            # Convert first 8 chars of hash to int (mod to keep it reasonable)
            fake_tmdb_id = int(title_hash[:8], 16) % 1000000
            required_fields['tmdbId'] = fake_tmdb_id
            logger.info(f"Added fake TMDB ID {fake_tmdb_id} for manual movie: {movie_data.get('title', '')}")
        
        try:
            result = self._make_request('POST', 'movie', required_fields)
            logger.info(f"Successfully added movie: {required_fields['title']}")
            return result
        except Exception as e:
            logger.error(f"Error adding movie: {str(e)}")
            return None
    
    def add_movie_manual(self, movie_data: Dict) -> Optional[Dict]:
        """Add a movie to Whisparr manually without external validation"""
        # Get the correct quality profile ID dynamically
        quality_profile_id = self._get_quality_profile_id()
        
        required_fields = {
            'title': movie_data.get('title'),
            'qualityProfileId': movie_data.get('qualityProfileId', quality_profile_id),
            'monitored': movie_data.get('monitored', True),
            'minimumAvailability': movie_data.get('minimumAvailability', 'released'),
            'rootFolderPath': movie_data.get('rootFolderPath', '/data/media/y'),
            'addOptions': movie_data.get('addOptions', {'searchForMovie': True})
        }
        
        # Add optional fields
        optional_fields = ['year', 'studio', 'overview', 'images', 'genres', 'ratings']
        for field in optional_fields:
            if field in movie_data:
                required_fields[field] = movie_data[field]
        
        try:
            result = self._make_request('POST', 'movie', required_fields)
            logger.info(f"Successfully added manual movie: {required_fields['title']}")
            return result
        except Exception as e:
            logger.error(f"Error adding manual movie: {str(e)}")
            return None
    
    def add_scene_as_movie(self, scene_data: Dict) -> Optional[Dict]:
        """Add a scene as a movie to Whisparr without StashDB validation"""
        # Convert scene data to movie format for Whisparr without StashDB ID
        movie_data = {
            'title': scene_data.get('title', 'Unknown Title'),
            'year': self._extract_year_from_date(scene_data.get('date')),
            'studio': scene_data.get('studio', {}).get('name', ''),
            'overview': scene_data.get('details', ''),
            'monitored': True,
            'qualityProfileId': scene_data.get('qualityProfileId', self._get_quality_profile_id()),
            'minimumAvailability': 'released',
            'rootFolderPath': scene_data.get('rootFolderPath', '/data/media/y'),
            'addOptions': {
                'searchForMovie': True
            }
        }
        
        # Add performer info to overview
        performers = scene_data.get('performers', [])
        if performers:
            performer_names = [p.get('performer', {}).get('name', '') for p in performers]
            if movie_data['overview']:
                movie_data['overview'] += f"\n\nPerformers: {', '.join(performer_names)}"
            else:
                movie_data['overview'] = f"Performers: {', '.join(performer_names)}"
        
        # Add tags as genres
        tags = scene_data.get('tags', [])
        if tags:
            movie_data['genres'] = [tag.get('name', '') for tag in tags]
        
        # Add duration info
        if scene_data.get('duration'):
            duration_minutes = scene_data['duration'] // 60
            movie_data['overview'] += f"\n\nDuration: {duration_minutes} minutes"
        
        # Add StashDB ID to overview instead of as identifier
        stashdb_id = scene_data.get('stashdb_id')
        if stashdb_id:
            movie_data['overview'] += f"\n\nStashDB ID: {stashdb_id}"
        
        return self.add_movie_manual(movie_data)
    
    def get_quality_profiles(self) -> List[Dict]:
        """Get quality profiles from Whisparr"""
        try:
            return self._make_request('GET', 'qualityprofile')
        except Exception as e:
            logger.error(f"Error getting quality profiles: {str(e)}")
            return []
    
    def get_root_folders(self) -> List[Dict]:
        """Get root folders from Whisparr"""
        try:
            return self._make_request('GET', 'rootfolder')
        except Exception as e:
            logger.error(f"Error getting root folders: {str(e)}")
            return []
    
    def check_movie_exists(self, title: str, year: int = None) -> bool:
        """Check if a movie already exists in Whisparr"""
        try:
            movies = self.get_movies()
            
            for movie in movies:
                if movie.get('title', '').lower() == title.lower():
                    if year is None or movie.get('year') == year:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking movie existence: {str(e)}")
            return False
    
    def get_wanted_movies(self) -> List[Dict]:
        """Get wanted movies from Whisparr"""
        try:
            return self._make_request('GET', 'wanted/missing')
        except Exception as e:
            logger.error(f"Error getting wanted movies: {str(e)}")
            return []
    
    def get_download_status(self, movie_id: int) -> Optional[Dict]:
        """Get download status for a specific movie"""
        try:
            return self._make_request('GET', f'movie/{movie_id}')
        except Exception as e:
            logger.error(f"Error getting download status: {str(e)}")
            return None
    
    def delete_movie(self, movie_id: int, delete_files: bool = False) -> bool:
        """Delete a movie from Whisparr"""
        try:
            endpoint = f'movie/{movie_id}'
            if delete_files:
                endpoint += '?deleteFiles=true'
            
            self._make_request('DELETE', endpoint)
            logger.info(f"Successfully deleted movie ID: {movie_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting movie: {str(e)}")
            return False
    
    def search_for_movie(self, movie_id: int) -> bool:
        """Trigger a search for a specific movie"""
        try:
            search_data = {
                'name': 'MoviesSearch',
                'movieIds': [movie_id]
            }
            
            self._make_request('POST', 'command', search_data)
            logger.info(f"Successfully triggered search for movie ID: {movie_id}")
            return True
        except Exception as e:
            logger.error(f"Error triggering movie search: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Whisparr"""
        try:
            self._make_request('GET', 'system/status')
            logger.info("Whisparr connection test successful")
            return True
        except Exception as e:
            logger.error(f"Whisparr connection test failed: {str(e)}")
            return False
    
    def _get_quality_profile_id(self) -> int:
        """Get the quality profile ID for 'Any' or fallback to the first available"""
        try:
            logger.info("Fetching quality profiles from Whisparr...")
            profiles = self.get_quality_profiles()
            logger.info(f"Found {len(profiles)} quality profiles: {[p.get('name') for p in profiles]}")
            
            # First try to find 'Any' profile
            for profile in profiles:
                profile_name = profile.get('name', '').lower()
                logger.info(f"Checking profile: '{profile_name}' (ID: {profile.get('id')})")
                if profile_name == 'any':
                    logger.info(f"Found 'Any' quality profile with ID: {profile['id']}")
                    return profile['id']
            
            # Fallback to first available profile
            if profiles:
                fallback_profile = profiles[0]
                logger.warning(f"'Any' quality profile not found, using first available: '{fallback_profile.get('name')}' (ID: {fallback_profile['id']})")
                return fallback_profile['id']
            
            # Last resort fallback
            logger.error("No quality profiles found, using default ID 1")
            return 1
            
        except Exception as e:
            logger.error(f"Error getting quality profile ID: {str(e)}")
            return 1
    
    def add_scene_by_uuid(self, stashdb_uuid: str, quality_profile_id: int = None, root_folder_path: str = None) -> Optional[Dict]:
        """Add a scene to Whisparr by StashDB UUID using the scene endpoint (bash script method)"""
        if not stashdb_uuid:
            logger.error("No StashDB UUID provided")
            return None
        
        try:
            # 1. Lookup the scene by UUID (exactly like bash script)
            logger.info(f"Looking up scene with UUID: {stashdb_uuid}")
            lookup_response = self._make_request('GET', f'lookup/scene?term={stashdb_uuid}')
            
            if not lookup_response or len(lookup_response) == 0:
                logger.warning(f"No scene found for UUID: {stashdb_uuid}")
                return None
            
            logger.info(f"Found scene lookup response with {len(lookup_response)} results")
            
            # 2. Build payload exactly like bash script: .[0].movie + {...}
            response_item = lookup_response[0]
            if 'movie' not in response_item:
                logger.error("No 'movie' key found in lookup response")
                return None
            
            scene_data = response_item['movie']
            logger.info(f"Extracted scene from movie wrapper: {scene_data.get('title', 'Unknown Title')}")
            
            # Get default values if not provided
            if quality_profile_id is None:
                quality_profile_id = self._get_quality_profile_id()
            
            if root_folder_path is None:
                root_folder_path = '/data/media/y'  # Default from your config
            
            # Build payload exactly like bash script: movie data + additional fields
            add_payload = scene_data.copy()
            add_payload.update({
                'qualityProfileId': quality_profile_id,
                'rootFolderPath': root_folder_path,
                'monitored': True
            })
            
            logger.info(f"Built payload with {len(add_payload)} fields for: {add_payload.get('title')}")
            logger.info(f"Payload keys: {list(add_payload.keys())}")
            
            # 3. POST to scene endpoint using URL params (like bash script)
            result = self._make_request('POST', 'scene', add_payload)
            
            if result:
                logger.info(f"Successfully added scene to Whisparr: {scene_data.get('title', 'Unknown')} (ID: {result.get('id')})")
                return result
            else:
                logger.warning("Scene endpoint returned no result, trying movie fallback...")
                # Fallback to movie method
                return self._add_scene_as_movie_fallback(scene_data, quality_profile_id, root_folder_path)
                
        except Exception as e:
            logger.error(f"Error adding scene by UUID {stashdb_uuid}: {str(e)}")
            # If scene method fails, try movie fallback
            try:
                logger.warning("Scene method failed, attempting movie fallback...")
                lookup_response = self._make_request('GET', f'lookup/scene?term={stashdb_uuid}')
                if lookup_response and len(lookup_response) > 0:
                    scene_data = lookup_response[0].get('movie', {})
                    if scene_data:
                        return self._add_scene_as_movie_fallback(scene_data, quality_profile_id or self._get_quality_profile_id(), root_folder_path or '/data/media/y')
            except Exception as fallback_error:
                logger.error(f"Movie fallback also failed: {str(fallback_error)}")
            
            return None
    
    def _add_scene_as_movie_fallback(self, scene_data: Dict, quality_profile_id: int, root_folder_path: str) -> Optional[Dict]:
        """Fallback method to add scene as movie when scene endpoint fails"""
        try:
            logger.info("Using movie endpoint fallback for scene addition")
            
            # Extract year from scene data properly
            year = None
            if scene_data.get('year'):
                year = int(scene_data['year'])
            elif scene_data.get('releaseDate'):
                try:
                    year = int(scene_data['releaseDate'][:4])
                except (ValueError, TypeError):
                    year = None
            
            # Convert scene data to movie format
            movie_data = {
                'title': scene_data.get('title', 'Unknown Title'),
                'qualityProfileId': quality_profile_id,
                'monitored': True,
                'minimumAvailability': 'released',
                'rootFolderPath': root_folder_path,
                'addOptions': {'searchForMovie': True}
            }
            
            # Only add year if we have a valid one
            if year and year > 1900 and year <= 2030:
                movie_data['year'] = year
            
            # Add studio if available
            if scene_data.get('studioTitle'):
                movie_data['studio'] = scene_data['studioTitle']
            
            # Build overview from scene data
            movie_data['overview'] = self._build_scene_overview(scene_data)
            
            # Add REQUIRED ForeignId field - use StashDB UUID
            foreign_id = scene_data.get('stashId') or scene_data.get('foreignId')
            if not foreign_id:
                logger.error("No StashDB UUID found in scene data for ForeignId")
                return None
            
            movie_data['foreignId'] = foreign_id
            
            # Add fake TMDB ID for Whisparr compatibility
            import hashlib
            title_hash = hashlib.md5(movie_data.get('title', '').encode()).hexdigest()
            fake_tmdb_id = int(title_hash[:8], 16) % 1000000
            movie_data['tmdbId'] = fake_tmdb_id
            
            logger.info(f"Adding as movie with ForeignId: {foreign_id}, TMDB ID: {fake_tmdb_id}, year: {movie_data.get('year', 'None')}")
            
            result = self._make_request('POST', 'movie', movie_data)
            
            if result:
                logger.info(f"Successfully added scene as movie: {movie_data['title']} (ID: {result.get('id')})")
                return result
            else:
                logger.error("Movie endpoint returned no result")
                return None
                
        except Exception as e:
            logger.error(f"Movie fallback also failed: {str(e)}")
            return None
    
    def _build_scene_overview(self, scene_data: Dict) -> str:
        """Build a detailed overview from scene data"""
        overview_parts = []
        
        # Add basic overview if available
        if scene_data.get('overview'):
            overview_parts.append(scene_data['overview'])
        
        # Add studio info
        if scene_data.get('studioTitle'):
            overview_parts.append(f"Studio: {scene_data['studioTitle']}")
        
        # Add performer info from credits
        credits = scene_data.get('credits', [])
        if credits:
            performer_names = [c.get('performer', {}).get('name', '') for c in credits if c.get('performer', {}).get('name')]
            if performer_names:
                overview_parts.append(f"Performers: {', '.join(performer_names)}")
        
        # Add runtime info
        if scene_data.get('runtime') and scene_data['runtime'] > 0:
            overview_parts.append(f"Duration: {scene_data['runtime']} minutes")
        
        # Add release date info
        if scene_data.get('releaseDate'):
            overview_parts.append(f"Release Date: {scene_data['releaseDate']}")
        
        # Add StashDB ID for reference
        if scene_data.get('stashId'):
            overview_parts.append(f"StashDB ID: {scene_data['stashId']}")
        
        return "\n\n".join(overview_parts) if overview_parts else "Adult scene from StashDB"
    
    def lookup_scene_by_uuid(self, stashdb_uuid: str) -> Optional[Dict]:
        """Lookup a scene in Whisparr by StashDB UUID without adding it"""
        try:
            # Try scene lookup first
            try:
                lookup_response = self._make_request('GET', f'lookup/scene?term={stashdb_uuid}')
                
                if lookup_response and len(lookup_response) > 0:
                    response_item = lookup_response[0]
                    # Extract from movie wrapper if present
                    if 'movie' in response_item:
                        return response_item['movie']
                    else:
                        return response_item
            except Exception as e:
                logger.warning(f"Scene lookup failed, trying movie lookup: {str(e)}")
                
                # Fallback to movie lookup
                try:
                    lookup_response = self._make_request('GET', f'movie/lookup?term={stashdb_uuid}')
                    
                    if lookup_response and len(lookup_response) > 0:
                        response_item = lookup_response[0]
                        # Extract from movie wrapper if present
                        if 'movie' in response_item:
                            return response_item['movie']
                        else:
                            return response_item
                except Exception as e2:
                    logger.warning(f"Movie lookup also failed: {str(e2)}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error looking up scene by UUID {stashdb_uuid}: {str(e)}")
            return None
    
    def check_scene_exists_by_uuid(self, stashdb_uuid: str) -> bool:
        """Check if a scene already exists in Whisparr by StashDB UUID"""
        try:
            # Get all scenes and check for matching StashDB ID
            scenes = self._make_request('GET', 'scene')
            
            if not scenes:
                return False
            
            for scene in scenes:
                # Check various possible StashDB ID fields
                scene_stashdb_id = (
                    scene.get('stashId') or 
                    scene.get('stashdb_id') or 
                    scene.get('foreignId') or
                    scene.get('stashdbId')
                )
                if scene_stashdb_id == stashdb_uuid:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking scene existence by UUID {stashdb_uuid}: {str(e)}")
            return False

    def _extract_year_from_date(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.year
                except ValueError:
                    continue
            
            # If none of the formats work, try to extract year with regex
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
            if year_match:
                return int(year_match.group())
            
        except Exception as e:
            logger.error(f"Error extracting year from date: {str(e)}")
        
        return None
