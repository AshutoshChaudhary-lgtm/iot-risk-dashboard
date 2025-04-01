import os
import re
import shodan
import time
import requests
import json
from urllib.parse import quote

class ShodanClient:
    def __init__(self, api_key=None, demo_mode=False):
        self.api_key = api_key or os.getenv("SHODAN_API_KEY")
        self.demo_mode = demo_mode
        
        if not self.api_key and not self.demo_mode:
            raise ValueError("No Shodan API key provided and demo mode is off")
        
        # Default to HTTP since your account doesn't support HTTPS
        self.use_https = False
        
        # Initialize the API client with your key
        try:
            # Set API host based on protocol
            if not self.use_https:
                shodan.Shodan.API_HOST = "http://api.shodan.io"
            
            self.api = shodan.Shodan(self.api_key)
            print(f"Initializing Shodan client with API key: {self.api_key[:5]}...")
        except Exception as e:
            print(f"Error initializing Shodan client: {e}")
            raise

    def search_devices(self, query, timeout=10):
        """Search for devices matching the query"""
        ip_regex = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
        
        # If query is a plain IP, try host lookup first
        if ip_regex.fullmatch(query):
            return self._process_ip_query(query, timeout)
        else:
            # Process as a search query
            return self._process_search_query(query, timeout)
    
    def _process_ip_query(self, ip, timeout=10):
        """Process a query that is a specific IP address"""
        print(f"Processing IP query: {ip}")
        
        # Try direct REST API requests with both HTTP and HTTPS
        results = self._try_direct_api_requests(ip, timeout)
        if results:
            print(f"Found {len(results)} devices using direct API request")
            return results
            
        # Try with the Shodan library
        try:
            print(f"Trying Shodan library host lookup for IP: {ip}")
            result = self.api.host(ip)
            print(f"Host lookup succeeded for {ip}")
            return [result]
        except shodan.APIError as e:
            print(f"Official library host lookup failed: {str(e)}")
            
            # If rate limited, try again after a delay
            if "request limit reached" in str(e).lower():
                print("API rate limit reached. Waiting 5 seconds before retry...")
                time.sleep(5)
                try:
                    result = self.api.host(ip)
                    return [result]
                except Exception as retry_err:
                    print(f"Retry failed: {retry_err}")
            
            # Try fallback search approach
            try:
                print(f"Trying fallback search for IP: {ip}")
                search_query = f"ip:{ip}"
                results = self.api.search(search_query)
                matches = results.get('matches', [])
                if matches:
                    print(f"Found {len(matches)} matches via search")
                    return matches
                else:
                    print("No matches found via search")
            except Exception as search_err:
                print(f"Fallback search failed: {search_err}")
        
        # If all attempts failed, return empty list
        print("All lookup methods failed, returning empty result")
        return []
    
    def _process_search_query(self, query, timeout=10):
        """Process a general search query"""
        print(f"Processing search query: {query}")
        
        try:
            # Execute the search
            results = self.api.search(query)
            matches = results.get('matches', [])
            print(f"Search found {len(matches)} matches")
            return matches
        except shodan.APIError as e:
            print(f"Search API error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected search error: {e}")
            return []
    
    def _try_direct_api_requests(self, ip, timeout=10):
    
    # Try different protocols - HTTP first since your account prefers it
        protocols = ["http", "https"]
        
        for protocol in protocols:
            try:
                # Make a direct request to the Shodan API
                url = f"{protocol}://api.shodan.io/shodan/host/{ip}?key={self.api_key}"
                print(f"Trying direct API request via {protocol.upper()}")
                
                response = requests.get(url, timeout=timeout)
                print(f"{protocol.upper()} direct API response status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"Direct {protocol.upper()} API access successful")
                    # If this works, update the protocol preference for the library
                    if protocol == "http" and self.use_https:
                        print("Switching to HTTP for future requests")
                        self.use_https = False
                        shodan.Shodan.API_HOST = "http://api.shodan.io"
                        # Reinitialize the API client with the new protocol
                        self.api = shodan.Shodan(self.api_key)
                    
                    try:
                        # Try to parse the response as JSON
                        result = response.json()
                        
                        # Ensure the result has proper location structure
                        if "country_name" in result and "city" in result:
                            # If location data is at root level, move it to location object
                            if "location" not in result or not isinstance(result["location"], dict):
                                result["location"] = {}
                            
                            # Move country and city data if not already in location
                            if "country_name" not in result["location"]:
                                result["location"]["country_name"] = result.get("country_name")
                            if "city" not in result["location"]:
                                result["location"]["city"] = result.get("city")
                            if "latitude" not in result["location"] and "longitude" not in result["location"]:
                                result["location"]["latitude"] = result.get("latitude")
                                result["location"]["longitude"] = result.get("longitude")
                                
                        print(f"Location data processed: {result.get('location')}")
                        return [result]
                    except json.JSONDecodeError:
                        print(f"Could not parse response as JSON: {response.text[:100]}...")
            except Exception as e:
                print(f"Direct {protocol.upper()} API request failed: {e}")
    
        # If we get here, all direct attempts failed
        return None

    def get_device_info(self, device_id, timeout=10):
        """Get detailed information about a specific device"""
        try:
            return self.api.host(device_id)
        except shodan.APIError as e:
            print(f"Error getting device info: {e}")
            return {}