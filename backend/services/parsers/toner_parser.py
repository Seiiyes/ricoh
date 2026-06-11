#!/usr/bin/env python3
"""
Toner Parser - Scrapes printer status page for toner levels
Handles cookie session login and parses getStatus.cgi HTML
"""
import requests
import re
from bs4 import BeautifulSoup
import urllib3
import logging
from .ricoh_auth import RicohAuthService

# Disable ssl warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

def get_printer_toner_levels(printer_ip: str) -> dict:
    """
    Retrieves toner levels from the printer's Web Image Monitor by scraping getStatus.cgi.
    
    Args:
        printer_ip: IP address of the printer
        
    Returns:
        dict: {
            'cyan': int,
            'magenta': int,
            'yellow': int,
            'black': int,
            'success': bool,
            'message': str
        }
    """
    session = requests.Session()
    session.verify = False
    
    # Standard browser headers to avoid detection or simple drops
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    })
    
    try:
        # Step 1: Authenticate with the printer
        logger.info(f"Authenticating with printer at {printer_ip} to get toner levels...")
        RicohAuthService.login_to_printer(session, printer_ip)
        
        # Step 2: Request the status page (getStatus.cgi)
        status_url = f"http://{printer_ip}/web/entry/es/websys/webArch/getStatus.cgi"
        headers = {
            'Referer': f'http://{printer_ip}/web/entry/es/websys/webArch/topPage.cgi'
        }
        
        logger.info(f"Fetching status page: {status_url}")
        resp = session.get(status_url, headers=headers, timeout=10)
        
        if resp.status_code != 200:
            return {
                'cyan': 0, 'magenta': 0, 'yellow': 0, 'black': 0,
                'success': False,
                'message': f"Printer returned HTTP status code {resp.status_code}"
            }
            
        # Step 3: Parse HTML
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Map of color to its corresponding image source filename suffix
        color_map = {
            'cyan': 'deviceStTnBarC.gif',
            'magenta': 'deviceStTnBarM.gif',
            'yellow': 'deviceStTnBarY.gif',
            'black': 'deviceStTnBarK.gif'
        }
        
        levels = {}
        found_any = False
        
        for color, img_suffix in color_map.items():
            img = soup.find('img', src=re.compile(re.escape(img_suffix)))
            if img:
                try:
                    width = int(img.get('width', 0))
                    # Normalizing to percentage (100% = 128px bar width in Ricoh MP series)
                    percentage = round((width / 128.0) * 100)
                    percentage = min(100, max(0, percentage))
                    
                    levels[color] = percentage
                    found_any = True
                    logger.info(f"Parsed {color} toner: {percentage}% (width {width}px)")
                except Exception as e:
                    logger.warning(f"Error parsing width for {color} toner: {e}")
                    levels[color] = 0
            else:
                logger.warning(f"Toner bar image {img_suffix} not found in HTML.")
                levels[color] = 0
                
        if found_any:
            levels['success'] = True
            levels['message'] = "Toner levels parsed successfully via Web Image Monitor"
            return levels
        else:
            return {
                'cyan': 0, 'magenta': 0, 'yellow': 0, 'black': 0,
                'success': False,
                'message': "Could not find any toner levels in getStatus.html"
            }
            
    except Exception as e:
        logger.error(f"Failed to scrape toner levels for printer {printer_ip}: {e}")
        return {
            'cyan': 0, 'magenta': 0, 'yellow': 0, 'black': 0,
            'success': False,
            'message': f"Scraping error: {str(e)}"
        }
