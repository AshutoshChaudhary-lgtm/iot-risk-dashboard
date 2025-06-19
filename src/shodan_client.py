import os
import re
import shodan
import time
import requests
import json
from urllib.parse import quote

class ShodanClient:
    def __init__(self, api_key=None, demo_mode=False):
        self.api_key = api_key
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
            
    def scan_ip(self, ip):
        """Request Shodan to scan a specific IP address
        Note: This requires a Shodan Pro membership
        """
        try:
            if self.demo_mode:
                return {"id": "demo123", "count": 1, "credits_left": 100}
            
            # Try official API first
            try:
                result = self.api.scan(ip)
                return result
            except Exception as e:
                print(f"Official scan API failed: {str(e)}")
                
            # Fallback to direct API request
            url = f"{'https' if self.use_https else 'http'}://api.shodan.io/shodan/scan?key={self.api_key}"
            response = requests.post(url, json={"ips": ip})
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Scan API request failed with status {response.status_code}")
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            print(f"Error in scan_ip: {str(e)}")
            if self.demo_mode:
                return {"id": "demo123", "count": 1, "credits_left": 100}
            return {"error": str(e)}

    def search_devices(self, query, timeout=10):
        """Search for devices matching the query"""
        ip_regex = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")
        
        # If query is a plain IP, try host lookup first
        if ip_regex.fullmatch(query):
            return self._process_ip_query(query, timeout)
        else:
            # Process as a search query
            return self._process_search_query(query, timeout)
    
    def get_domain_info(self, domain):
        """Get information about a domain using Shodan DNS API"""
        try:
            if self.demo_mode:
                return {
                    "domain": domain,
                    "subdomains": ["www", "mail", "remote", "login"],
                    "tags": ["cms", "e-commerce"],
                    "ports": [80, 443, 8080, 25]
                }
                
            # Try official API first
            try:
                # Get DNS information
                dns_info = self.api.dns.domain_info(domain)
                
                # Get DNS resolution
                ip = self.api.dns.resolve(domain)
                
                # Enrich with DNS resolution data
                dns_info["resolution"] = ip
                
                return dns_info
            except Exception as e:
                print(f"Official domain API failed: {str(e)}")
                
            # Fallback to direct request
            url = f"{'https' if self.use_https else 'http'}://api.shodan.io/dns/domain/{domain}?key={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Domain API request failed with status {response.status_code}")
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            print(f"Error in get_domain_info: {str(e)}")
            if self.demo_mode:
                return {
                    "domain": domain,
                    "subdomains": ["www", "mail", "remote", "login"],
                    "tags": ["cms", "e-commerce"],
                    "ports": [80, 443, 8080, 25]
                }
            return {"error": str(e)}
    
    def create_network_alert(self, name, ip_network, triggers=None):
        """Create a new network alert for a CIDR range
        
        Args:
            name (str): Name of the alert
            ip_network (str): Network range in CIDR notation (e.g., "192.168.1.0/24")
            triggers (list): List of trigger names (e.g., ["malware", "open_database"])
            
        Returns:
            dict: Alert creation result or error message
        """
        try:
            if self.demo_mode:
                return {"id": "demo123", "name": name, "filters": {"ip": ip_network}}
                
            # Set default triggers if none provided
            if not triggers:
                triggers = ["malware", "open_database", "ssl_expired", "industrial_control_system"]
                
            # Try official API first
            try:
                # Create the alert
                result = self.api.create_alert(name=name, ip=ip_network, triggers=triggers)
                return result
            except Exception as e:
                print(f"Official create alert API failed: {str(e)}")
                
            # Fallback to direct request
            url = f"{'https' if self.use_https else 'http'}://api.shodan.io/shodan/alert?key={self.api_key}"
            data = {
                "name": name,
                "filters": {
                    "ip": ip_network
                },
                "triggers": triggers
            }
            
            response = requests.post(url, json=data)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"Create alert API request failed with status {response.status_code}")
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            print(f"Error creating network alert: {str(e)}")
            if self.demo_mode:
                return {"id": "demo123", "name": name, "filters": {"ip": ip_network}}
            return {"error": str(e)}
            
    def list_alerts(self):
        """List all configured network alerts"""
        try:
            if self.demo_mode:
                return [
                    {"id": "demo123", "name": "Corporate Network", "created": "2025-06-07"},
                    {"id": "demo456", "name": "IoT Devices", "created": "2025-06-08"}
                ]
                
            # Try official API first
            try:
                alerts = self.api.alerts()
                return alerts
            except Exception as e:
                print(f"Official alerts API failed: {str(e)}")
                
            # Fallback to direct request
            url = f"{'https' if self.use_https else 'http'}://api.shodan.io/shodan/alert/info?key={self.api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"List alerts API request failed with status {response.status_code}")
                return {"error": f"API request failed with status {response.status_code}"}
                
        except Exception as e:
            print(f"Error listing alerts: {str(e)}")
            if self.demo_mode:
                return [
                    {"id": "demo123", "name": "Corporate Network", "created": "2025-06-07"},
                    {"id": "demo456", "name": "IoT Devices", "created": "2025-06-08"}
                ]
            return {"error": str(e)}
    
    def get_exposure_report(self, domain):
        """Get an internet exposure report for an organization
        
        Args:
            domain (str): Domain name of the organization
            
        Returns:
            dict: Report data or error message
        """
        try:
            if self.demo_mode:
                return {
                    "domain": domain,
                    "ports": {"80": 15, "443": 10, "22": 5, "21": 2},
                    "vulnerabilities": ["CVE-2021-44228", "CVE-2022-22965"],
                    "services": {"http": 20, "ssh": 5, "ftp": 2},
                    "total_ips": 32
                }
                
            # First get domain info to find related IPs
            domain_info = self.get_domain_info(domain)
            
            # Initialize report structure
            report = {
                "domain": domain,
                "ports": {},
                "vulnerabilities": [],
                "services": {},
                "total_ips": 0,
                "countries": {},
                "timestamps": []
            }
            
            # Try official API first
            try:
                # Search for all devices under this domain
                query = f"hostname:{domain}"
                search_results = self.api.search(query)
                
                # Process results
                if "matches" in search_results:
                    report["total_ips"] = search_results.get("total", 0)
                    
                    # Process each result
                    for match in search_results["matches"]:
                        # Count ports
                        port = match.get("port")
                        if port:
                            report["ports"][str(port)] = report["ports"].get(str(port), 0) + 1
                        
                        # Count services
                        service = match.get("_shodan", {}).get("module")
                        if service:
                            report["services"][service] = report["services"].get(service, 0) + 1
                            
                        # Collect timestamps
                        timestamp = match.get("timestamp")
                        if timestamp and timestamp not in report["timestamps"]:
                            report["timestamps"].append(timestamp)
                            
                        # Count countries
                        country = match.get("location", {}).get("country_name")
                        if country:
                            report["countries"][country] = report["countries"].get(country, 0) + 1
                            
                        # Collect vulnerabilities
                        vulns = match.get("vulns", {})
                        if vulns:
                            for vuln_id in vulns:
                                if vuln_id not in report["vulnerabilities"]:
                                    report["vulnerabilities"].append(vuln_id)
                
                return report
            except Exception as e:
                print(f"Official search API for exposure report failed: {str(e)}")
                
            # Fallback to demo mode if all else fails
            return {
                "domain": domain,
                "ports": {"80": 15, "443": 10, "22": 5, "21": 2},
                "vulnerabilities": ["CVE-2021-44228", "CVE-2022-22965"],
                "services": {"http": 20, "ssh": 5, "ftp": 2},
                "total_ips": 32,
                "note": "Using demo data due to API limitations"
            }
                
        except Exception as e:
            print(f"Error generating exposure report: {str(e)}")
            if self.demo_mode:
                return {
                    "domain": domain,
                    "ports": {"80": 15, "443": 10, "22": 5, "21": 2},
                    "vulnerabilities": ["CVE-2021-44228", "CVE-2022-22965"],
                    "services": {"http": 20, "ssh": 5, "ftp": 2},
                    "total_ips": 32
                }
            return {"error": str(e)}
            
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