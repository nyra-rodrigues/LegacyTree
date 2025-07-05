from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="legacytree_app")
    
    def get_coordinates(self, location: str) -> tuple[float, float]:
        """
        Convert location string to (latitude, longitude)
        Returns default coordinates (Toronto) if geocoding fails
        """
        try:
            # Add a small delay to be respectful to the geocoding service
            time.sleep(1)
            
            location_data = self.geolocator.geocode(location)
            
            if location_data:
                return (location_data.latitude, location_data.longitude)
            else:
                # Default to Toronto if location not found
                print(f"Location '{location}' not found, using default coordinates")
                return (43.6532, -79.3832)
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error for '{location}': {e}")
            # Default to Toronto on error
            return (43.6532, -79.3832)
    
    def get_location_info(self, location: str) -> dict:
        """
        Get detailed location information
        """
        try:
            time.sleep(1)
            location_data = self.geolocator.geocode(location)
            
            if location_data:
                return {
                    "latitude": location_data.latitude,
                    "longitude": location_data.longitude,
                    "address": location_data.address,
                    "raw": location_data.raw
                }
            else:
                return {
                    "latitude": 43.6532,
                    "longitude": -79.3832,
                    "address": "Toronto, Canada",
                    "raw": None
                }
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")
            return {
                "latitude": 43.6532,
                "longitude": -79.3832,
                "address": "Toronto, Canada",
                "raw": None
            } 