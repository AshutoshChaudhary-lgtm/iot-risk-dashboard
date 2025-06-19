from fastapi import APIRouter, HTTPException
from src.utils.dns_lookup import DnsLookup
import os
import traceback

router = APIRouter()

@router.get("/resolve/{domain}")
async def resolve_domain(domain: str):
    """Resolve domain to IP addresses using Shodan DNS API"""
    try:
        dns_lookup = DnsLookup()
        ip_addresses = dns_lookup.resolve_domain(domain)
        
        if ip_addresses:
            return {"domain": domain, "ip_addresses": ip_addresses}
        else:
            raise HTTPException(status_code=404, detail=f"Could not resolve domain: {domain}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error resolving domain: {str(e)}")

@router.get("/reverse")
async def reverse_lookup(ips: str):
    """Perform reverse DNS lookup for IP addresses"""
    try:
        dns_lookup = DnsLookup()
        hostnames = dns_lookup.reverse_lookup(ips)
        
        return {"ip_hostnames": hostnames}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error performing reverse lookup: {str(e)}")

@router.get("/domain-info/{domain}")
async def domain_info(domain: str):
    """Get information about a domain"""
    try:
        dns_lookup = DnsLookup()
        info = dns_lookup.domain_info(domain)
        
        if not info:
            raise HTTPException(status_code=404, detail=f"No information found for domain: {domain}")
            
        return info
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting domain info: {str(e)}")
