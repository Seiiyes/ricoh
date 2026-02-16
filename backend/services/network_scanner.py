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
        
        Args:
            ip: IP address to resolve
            
        Returns:
            Hostname if resolved, None otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            hostname = await loop.run_in_executor(
                None,
                lambda: socket.gethostbyaddr(ip)[0]
            )
            return hostname
        except (socket.herror, socket.gaierror, OSError):
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
        hostname = await self.resolve_hostname(ip)
        
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
            if not hostname:
                hostname = f"printer-{ip.replace('.', '-')}"
        
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
            
            device_info = {
                "ip_address": ip,
                "hostname": hostname or f"printer-{ip.replace('.', '-')}",
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
