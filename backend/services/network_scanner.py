"""
Network scanning service for printer discovery
Async implementation for concurrent IP scanning with SNMP support
"""
import asyncio
import socket
from typing import List, Dict, Optional, Tuple
import ipaddress

from .snmp_client import get_snmp_client


class NetworkScanner:
    """
    Asynchronous network scanner for Ricoh printer discovery
    """
    
    def __init__(self, timeout: float = 1.0, enable_snmp: bool = True):
        """
        Initialize scanner
        
        Args:
            timeout: Connection timeout in seconds
            enable_snmp: Enable SNMP queries for detailed printer info
        """
        self.timeout = timeout
        self.enable_snmp = enable_snmp
        self.snmp_client = get_snmp_client() if enable_snmp else None
    
    async def check_port(self, ip: str, port: int) -> bool:
        """
        Check if a port is open on given IP
        
        Args:
            ip: IP address to check
            port: Port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout=self.timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False
    
    async def resolve_hostname(self, ip: str) -> Optional[str]:
        """
        Resolve hostname from IP address
        Only attempts DNS for IP .248 (problematic Kyocera printer)
        
        Args:
            ip: IP address to resolve
            
        Returns:
            Hostname if resolved, None otherwise
        """
        try:
            # Only do DNS lookup for .248 (the problematic Kyocera)
            if ip != "192.168.91.248":
                return None
            
            # Use async with longer timeout for this specific IP
            loop = asyncio.get_event_loop()
            hostname = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: socket.gethostbyaddr(ip)[0]
                ),
                timeout=8.0  # 8 second timeout for .248
            )
            return hostname
        except (socket.herror, socket.gaierror, OSError, asyncio.TimeoutError):
            return None
    
    async def get_ricoh_serial(self, ip: str) -> Optional[str]:
        """
        Get serial number (ID máquina) from Ricoh web interface
        
        Args:
            ip: IP address of printer
            
        Returns:
            Serial number if found, None otherwise
        """
        try:
            import requests
            import re
            from bs4 import BeautifulSoup
            
            loop = asyncio.get_event_loop()
            
            def fetch_serial():
                try:
                    # Try to access device information page
                    # Common Ricoh paths for device info
                    paths = [
                        "/web/guest/es/websys/status/configuration.cgi",
                        "/web/guest/en/websys/status/configuration.cgi",
                        "/web/guest/es/websys/webArch/mainFrame.cgi",
                    ]
                    
                    print(f"   Probando {len(paths)} rutas para obtener serial de {ip}...")
                    
                    for path in paths:
                        try:
                            url = f"http://{ip}{path}"
                            print(f"   Intentando: {url}")
                            response = requests.get(url, timeout=3)
                            
                            if response.status_code == 200:
                                print(f"   ✅ Respuesta OK de {path}")
                                
                                # Look for "ID máquina" or "Machine ID" patterns
                                # Pattern 1: ID máquina: E174M210096
                                match = re.search(r'ID\s+m[áa]quina[:\s]+([A-Z0-9]+)', response.text, re.IGNORECASE)
                                if match:
                                    serial = match.group(1).strip()
                                    print(f"✅ Found Ricoh serial (ID máquina): {serial} for {ip}")
                                    return serial
                                
                                # Pattern 2: Machine ID: E174M210096
                                match = re.search(r'Machine\s+ID[:\s]+([A-Z0-9]+)', response.text, re.IGNORECASE)
                                if match:
                                    serial = match.group(1).strip()
                                    print(f"✅ Found Ricoh serial (Machine ID): {serial} for {ip}")
                                    return serial
                                
                                # Pattern 3: Serial Number in HTML
                                match = re.search(r'Serial\s+Number[:\s]+([A-Z0-9]+)', response.text, re.IGNORECASE)
                                if match:
                                    serial = match.group(1).strip()
                                    print(f"✅ Found Ricoh serial (Serial Number): {serial} for {ip}")
                                    return serial
                                
                                # Pattern 4: Try parsing with BeautifulSoup for structured data
                                soup = BeautifulSoup(response.text, 'html.parser')
                                
                                # Look for table cells or divs containing "ID máquina"
                                for element in soup.find_all(['td', 'div', 'span']):
                                    text = element.get_text(strip=True)
                                    if 'ID máquina' in text or 'Machine ID' in text:
                                        # Try to find the value in next sibling or same element
                                        next_elem = element.find_next_sibling()
                                        if next_elem:
                                            serial_text = next_elem.get_text(strip=True)
                                            match = re.search(r'([A-Z0-9]{10,})', serial_text)
                                            if match:
                                                serial = match.group(1)
                                                print(f"✅ Found Ricoh serial (parsed): {serial} for {ip}")
                                                return serial
                                
                                print(f"   ⚠️  No se encontró patrón de serial en {path}")
                            else:
                                print(f"   ❌ Status {response.status_code} en {path}")
                        except Exception as e:
                            print(f"   ❌ Error en {path}: {e}")
                            continue
                    
                    print(f"⚠️  No serial number found for {ip} después de probar todas las rutas")
                    return None
                            
                except Exception as e:
                    print(f"❌ Error fetching serial from {ip}: {e}")
                    return None
            
            serial = await loop.run_in_executor(None, fetch_serial)
            return serial
            
        except Exception as e:
            print(f"❌ Error in get_ricoh_serial for {ip}: {e}")
            return None
    
    async def get_ricoh_hostname(self, ip: str) -> Optional[str]:
        """
        Get hostname from Ricoh/Kyocera web interface by parsing the HTML
        
        Args:
            ip: IP address of printer
            
        Returns:
            Hostname if found, None otherwise
        """
        try:
            import requests
            import re
            
            loop = asyncio.get_event_loop()
            
            def fetch_hostname():
                try:
                    # Try Ricoh mainFrame first (fastest for Ricoh printers)
                    try:
                        response = requests.get(f"http://{ip}/web/guest/es/websys/webArch/mainFrame.cgi", timeout=3)
                        if response.status_code == 200:
                            match = re.search(r'<title>\s*([A-Z0-9]+)\s*-\s*Web Image Monitor\s*</title>', response.text, re.IGNORECASE)
                            if match:
                                hostname = match.group(1).strip()
                                print(f"✅ Found Ricoh hostname: {hostname} for {ip}")
                                return hostname
                    except:
                        pass
                    
                    # Try Kyocera Start_Wlm.htm
                    try:
                        response = requests.get(f"http://{ip}/startwlm/Start_Wlm.htm", timeout=10)
                        if response.status_code == 200:
                            # Use the same pattern as debug script - group(2) is hostname
                            match = re.search(r'HeaderStatusPC\s*\(\s*"([^"]*)"\s*,\s*"([A-Z0-9]+)"\s*,', response.text, re.IGNORECASE)
                            if match:
                                hostname = match.group(2).strip()
                                print(f"✅ Found Kyocera hostname: {hostname} for {ip}")
                                return hostname
                    except:
                        pass
                    
                    # Try Kyocera index.html (fallback for some models)
                    try:
                        response = requests.get(f"http://{ip}/index.html", timeout=10)
                        if response.status_code == 200:
                            # Use the same pattern as debug script
                            match = re.search(r'HeaderStatusPC\s*\(\s*"([^"]*)"\s*,\s*"([A-Z0-9]+)"\s*,', response.text, re.IGNORECASE)
                            if match:
                                hostname = match.group(2).strip()  # group(2) is the hostname
                                print(f"✅ Found Kyocera hostname in index.html: {hostname} for {ip}")
                                return hostname
                    except:
                        pass
                    
                    # Try Kyocera Device_Config.model.htm (for newer Kyocera models)
                    try:
                        response = requests.get(f"http://{ip}/js/jssrc/model/startwlm/Device_Config.model.htm", timeout=3)
                        if response.status_code == 200:
                            # Look for hostname patterns in JavaScript
                            match = re.search(r'["\']?hostname["\']?\s*[:=]\s*["\']([A-Z0-9]+)["\']', response.text, re.IGNORECASE)
                            if match:
                                hostname = match.group(1).strip()
                                print(f"✅ Found Kyocera hostname in Device_Config: {hostname} for {ip}")
                                return hostname
                            # Look for KM pattern
                            match = re.search(r'KM[A-F0-9]{6,12}', response.text, re.IGNORECASE)
                            if match:
                                hostname = match.group(0)
                                print(f"✅ Found Kyocera pattern in Device_Config: {hostname} for {ip}")
                                return hostname
                    except:
                        pass
                    
                    # Fallback: check root page for Kyocera
                    try:
                        response = requests.get(f"http://{ip}", timeout=3)
                        if response.status_code == 200:
                            # Check if it's Kyocera
                            if 'KYOCERA' in response.text.upper():
                                # Try to find KM pattern
                                match = re.search(r'KM[A-F0-9]{6,12}', response.text, re.IGNORECASE)
                                if match:
                                    hostname = match.group(0)
                                    print(f"✅ Found Kyocera pattern: {hostname} for {ip}")
                                    return hostname
                                # If no pattern found, use descriptive name
                                hostname = f"Kyocera-{ip.replace('.', '-')}"
                                print(f"✅ Detected Kyocera: {hostname} for {ip}")
                                return hostname
                    except:
                        pass
                    
                    print(f"⚠️  No hostname found for {ip}")
                            
                except Exception as e:
                    print(f"❌ Error fetching hostname from {ip}: {e}")
                return None
            
            hostname = await loop.run_in_executor(None, fetch_hostname)
            return hostname
            
        except Exception as e:
            print(f"❌ Error in get_ricoh_hostname for {ip}: {e}")
            return None
    
    async def detect_printer(self, ip: str) -> Tuple[bool, Optional[Dict]]:
        """
        Detect if device is a printer by checking printer-specific indicators
        
        Args:
            ip: IP address to check
            
        Returns:
            Tuple of (is_printer, device_info)
        """
        # Check common printer ports
        http_open = await self.check_port(ip, 80)      # Web interface
        https_open = await self.check_port(ip, 443)    # Secure web interface
        snmp_open = await self.check_port(ip, 161)     # SNMP management
        raw_print = await self.check_port(ip, 9100)    # Raw printing (JetDirect) - PRINTER SPECIFIC
        
        # Get hostname for identification
        # Try DNS resolution first (most reliable for Windows networks)
        hostname = await self.resolve_hostname(ip)
        
        # If DNS failed, try web interface as fallback
        if not hostname and (http_open or https_open):
            hostname = await self.get_ricoh_hostname(ip)
        
        # Determine if it's a printer based on strict criteria
        is_printer = False
        model = "Unknown Printer"
        has_color = False
        has_scanner = False
        
        # Check if hostname indicates it's a printer
        if hostname:
            hostname_lower = hostname.lower()
            
            # Printer keywords - must match at least one
            printer_keywords = ['ricoh', 'printer', 'print', 'mfp', 'copier', 'mp', 'sp', 'im', 'laserjet', 'deskjet']
            has_printer_keyword = any(keyword in hostname_lower for keyword in printer_keywords)
            
            if has_printer_keyword:
                is_printer = True
                
                # Detect Ricoh brand and model
                if 'ricoh' in hostname_lower:
                    # Extract model from hostname
                    if 'mp' in hostname_lower:
                        model = "RICOH MP Series"
                        has_color = True
                        has_scanner = True
                    elif 'sp' in hostname_lower:
                        model = "RICOH SP Series"
                        has_color = False
                        has_scanner = False
                    elif 'im' in hostname_lower:
                        model = "RICOH IM Series"
                        has_color = True
                        has_scanner = True
                    else:
                        model = "RICOH Printer"
                        has_color = True
                        has_scanner = True
                else:
                    # Generic printer with keyword in hostname
                    model = "Network Printer"
                    has_color = False
                    has_scanner = http_open or https_open
        
        # Port 9100 is VERY specific to printers (JetDirect/raw printing)
        # If this port is open, it's almost certainly a printer
        if raw_print and not is_printer:
            is_printer = True
            model = "Network Printer (Port 9100)"
            has_scanner = http_open or https_open
            # Don't override hostname if we already have one from web interface
            # Only set generic name if we truly have no hostname
        
        # If we determined it's a printer, return device info
        if is_printer:
            # Try to get detailed info via SNMP if enabled
            toner_black = 0
            toner_cyan = 0
            toner_magenta = 0
            toner_yellow = 0
            serial_number = None
            detected_location = None
            
            if self.enable_snmp and self.snmp_client:
                try:
                    snmp_info = await self.snmp_client.get_printer_info(ip)
                    
                    # Use SNMP data if available
                    if snmp_info.model:
                        model = snmp_info.model
                    if snmp_info.serial_number:
                        serial_number = snmp_info.serial_number
                    if snmp_info.location:
                        detected_location = snmp_info.location
                    
                    # Get toner levels from SNMP
                    if snmp_info.toner_black is not None:
                        toner_black = snmp_info.toner_black
                    if snmp_info.toner_cyan is not None:
                        toner_cyan = snmp_info.toner_cyan
                    if snmp_info.toner_magenta is not None:
                        toner_magenta = snmp_info.toner_magenta
                    if snmp_info.toner_yellow is not None:
                        toner_yellow = snmp_info.toner_yellow
                        
                except Exception as e:
                    # SNMP failed, continue with basic detection
                    print(f"SNMP query failed for {ip}: {str(e)}")
            
            # If SNMP didn't get serial, try web interface (Ricoh only)
            if not serial_number and 'ricoh' in model.lower():
                try:
                    print(f"🔍 Intentando obtener serial desde web para {ip}...")
                    serial_number = await self.get_ricoh_serial(ip)
                    if serial_number:
                        print(f"✅ Serial obtenido: {serial_number}")
                    else:
                        print(f"⚠️  No se pudo obtener serial desde web para {ip}")
                except Exception as e:
                    print(f"❌ Web serial query failed for {ip}: {str(e)}")
            
            # Use detected hostname, or fallback to generic name only if no hostname found
            final_hostname = hostname if hostname else f"printer-{ip.replace('.', '-')}"
            
            device_info = {
                "ip_address": ip,
                "hostname": final_hostname,
                "status": "online",
                "detected_model": model,
                "serial_number": serial_number,
                "has_color": has_color or (toner_cyan > 0 or toner_magenta > 0 or toner_yellow > 0),
                "has_scanner": has_scanner,
                "has_fax": False,
                "toner_cyan": toner_cyan,
                "toner_magenta": toner_magenta,
                "toner_yellow": toner_yellow,
                "toner_black": toner_black,
                "location": detected_location
            }
            return True, device_info
        
        return False, None
    
    async def scan_single_ip(self, ip: str) -> Optional[Dict]:
        """
        Scan a single IP address
        
        Args:
            ip: IP address to scan
            
        Returns:
            Device info dict if printer found, None otherwise
        """
        is_printer, device_info = await self.detect_printer(ip)
        return device_info if is_printer else None
    
    async def scan_network(self, ip_range: str, max_concurrent: int = 50) -> List[Dict]:
        """
        Scan a network range for printers
        
        Args:
            ip_range: CIDR notation IP range (e.g., 192.168.1.0/24)
            max_concurrent: Maximum concurrent scans
            
        Returns:
            List of discovered printer devices
        """
        network = ipaddress.ip_network(ip_range, strict=False)
        
        # Limit scan to reasonable subnet sizes
        if network.num_addresses > 256:
            raise ValueError("IP range too large. Maximum 256 addresses (/24 subnet)")
        
        # Create semaphore to limit concurrent connections
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scan_with_semaphore(ip: str):
            async with semaphore:
                return await self.scan_single_ip(ip)
        
        # Create tasks for all IPs in range
        tasks = [scan_with_semaphore(str(ip)) for ip in network.hosts()]
        
        # Execute all scans concurrently
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        devices = [device for device in results if device is not None]
        
        return devices

    async def check_single_device(self, ip: str, snmp_port: int = 161) -> Optional[Dict]:
        """
        Check a single device by IP and return printer information
        
        Args:
            ip: IP address to check
            snmp_port: SNMP port (default 161)
            
        Returns:
            Device information dict if it's a printer, None otherwise
        """
        try:
            # Check if device is reachable on port 80 (web interface)
            is_reachable = await self.check_port(ip, 80)
            
            if not is_reachable:
                return None
            
            # Try to detect if it's a printer
            is_printer, device_info = await self.detect_printer(ip)
            
            if is_printer and device_info:
                return device_info
            
            return None
            
        except Exception as e:
            print(f"Error checking device {ip}: {e}")
            return None
