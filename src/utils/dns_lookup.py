"""
Integration with Shodan's DNS API to resolve domains and lookup domain information
"""
import requests
import os
import json

class DnsLookup:
    def __init__(self, api_key=None):
        """Initialize the DNS Lookup with Shodan API key"""
        self.api_key = api_key or os.getenv("SHODAN_API_KEY")
        
        if not self.api_key:
            raise ValueError("No Shodan API key provided for DNS lookup")
            
    def resolve_domain(self, domain):
        """
        Resolve domain to IP addresses
        
        Parameters:
        - domain: Domain name to resolve
        
        Returns: List of IP addresses
        """
        try:
            url = f"https://api.shodan.io/dns/resolve?hostnames={domain}&key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                # Result is a dict with domain as key and IP as value
                return result.get(domain)
            else:
                print(f"Failed to resolve domain. Status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error resolving domain {domain}: {e}")
            return None
            
    def reverse_lookup(self, ip_addresses):
        """
        Perform reverse DNS lookup for IP addresses
        
        Parameters:
        - ip_addresses: List or comma-separated string of IP addresses
        
        Returns: Dictionary of IP addresses to hostnames
        """
        if isinstance(ip_addresses, list):
            ip_addresses = ",".join(ip_addresses)
            
        try:
            url = f"https://api.shodan.io/dns/reverse?ips={ip_addresses}&key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to perform reverse lookup. Status code: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Error performing reverse lookup for {ip_addresses}: {e}")
            return {}
            
    def domain_info(self, domain):
        """
        Get domain information
        
        Parameters:
        - domain: Domain name to lookup
        
        Returns: Domain information
        """
        try:
            url = f"https://api.shodan.io/dns/domain/{domain}?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get domain info. Status code: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Error getting domain info for {domain}: {e}")
            return {}
