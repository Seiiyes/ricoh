"""
Ricoh Web Interface Client
Sends user configuration to Ricoh printers via HTTP/Web interface
"""
import requests
from typing import Dict, Optional
import logging
from bs4 import BeautifulSoup
import re
import base64

logger = logging.getLogger(__name__)


class RicohWebClient:
    """
    Client for provisioning users to Ricoh printers via web interface
    """
    
    def __init__(self, timeout: int = 30, admin_user: str = "admin", admin_password: str = ""):
        """
        Initialize Ricoh web client
        
        Args:
            timeout: Request timeout in seconds
            admin_user: Administrator username (default: "admin")
            admin_password: Administrator password (default: empty)
        """
        self.timeout = timeout
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.session = requests.Session()
        # Disable SSL verification for self-signed certificates
        self.session.verify = False
        # Store authenticated sessions per printer IP
        self._authenticated_printers = set()
    
    def _get_login_token(self, printer_ip: str) -> Optional[str]:
        """
        Get wimToken from login page
        
        Args:
            printer_ip: Printer IP address
            
        Returns:
            wimToken or None
        """
        try:
            login_page_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
            response = self.session.get(login_page_url, timeout=self.timeout)
            
            if response.status_code == 200:
                match = re.search(r'name="wimToken"\s+value="(\d+)"', response.text)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.debug(f"Error obteniendo login token: {e}")
            return None
    
    def _authenticate(self, printer_ip: str) -> bool:
        """
        Authenticate with the printer to get session cookies
        
        Args:
            printer_ip: Printer IP address
            
        Returns:
            True if authentication successful, False otherwise
        """
        # Check if already authenticated
        if printer_ip in self._authenticated_printers:
            return True
        
        try:
            logger.info(f"🔐 Autenticando con impresora {printer_ip}...")
            
            # Step 1: Try to access the address list page
            test_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            test_response = self.session.get(test_url, timeout=self.timeout, allow_redirects=False)
            
            # If we get 200, we're already authenticated or no auth needed
            if test_response.status_code == 200 and 'wimToken' in test_response.text:
                logger.info(f"✅ Ya autenticado o sin autenticación requerida")
                self._authenticated_printers.add(printer_ip)
                return True
            
            # Need to login
            logger.info(f"🔑 Realizando login con usuario: {self.admin_user}")
            
            # Step 2: Get wimToken from login page
            login_token = self._get_login_token(printer_ip)
            if not login_token:
                logger.error(f"❌ No se pudo obtener wimToken de la página de login")
                return False
            
            logger.debug(f"Login wimToken obtenido: {login_token}")
            
            # Step 3: Encode credentials in Base64
            userid_b64 = base64.b64encode(self.admin_user.encode()).decode()
            password_b64 = base64.b64encode(self.admin_password.encode()).decode() if self.admin_password else ""
            
            # Step 4: Perform login
            login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
            login_data = {
                'wimToken': login_token,
                'userid_work': '',
                'userid': userid_b64,
                'password_work': '',
                'password': password_b64,
                'open': '',
            }
            
            login_response = self.session.post(
                login_url,
                data=login_data,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Step 5: Verify authentication by accessing protected page
            verify_response = self.session.get(test_url, timeout=self.timeout)
            if verify_response.status_code == 200 and 'wimToken' in verify_response.text:
                logger.info(f"✅ Autenticación exitosa")
                self._authenticated_printers.add(printer_ip)
                return True
            
            logger.error(f"❌ Autenticación fallida")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error durante autenticación: {e}")
            return False
    
    def provision_user(self, printer_ip: str, user_config: Dict) -> bool:
        """
        Provision a user to a Ricoh printer via web interface
        
        Args:
            printer_ip: Printer IP address
            user_config: User configuration dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n{'='*70}")
            print(f"🔄 ricoh_web_client.provision_user() INICIADO")
            print(f"   Versión: SIN entryIndexIn (autoincremental)")
            print(f"   Impresora: {printer_ip}")
            print(f"   Usuario: {user_config.get('nombre')}")
            print(f"{'='*70}\n")
            
            logger.info(f"🔄 Provisioning user to Ricoh printer at {printer_ip}")
            logger.info(f"   User: {user_config.get('nombre')} (Code: {user_config.get('codigo_de_usuario')})")
            
            # Step 1: Authenticate
            if not self._authenticate(printer_ip):
                logger.error("✗ Cannot proceed without authentication")
                return False
            
            # Step 2: Get wimToken from list page
            list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            logger.info(f"🔍 Paso 1: Obteniendo wimToken desde lista: {list_url}")
            
            list_response = self.session.get(list_url, timeout=self.timeout)
            if list_response.status_code != 200:
                logger.error(f"✗ Cannot access list page: {list_response.status_code}")
                return False
            
            # Extract wimToken from list
            match = re.search(r'name="wimToken"\s+value="(\d+)"', list_response.text)
            if not match:
                logger.error("✗ Cannot find wimToken in list page")
                return False
            
            list_wim_token = match.group(1)
            logger.info(f"✅ wimToken de lista obtenido: {list_wim_token}")
            
            # Step 3: POST to adrsGetUser.cgi to get the add user form (with fresh wimToken)
            get_user_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
            logger.info(f"🔍 Paso 2: Obteniendo formulario de añadir usuario: {get_user_url}")
            
            get_user_data = {
                'mode': 'ADDUSER',
                'outputSpecifyModeIn': 'DEFAULT',
                'wimToken': list_wim_token
            }
            
            form_response = self.session.post(
                get_user_url,
                data=get_user_data,
                timeout=self.timeout
            )
            
            if form_response.status_code != 200:
                logger.error(f"✗ Cannot get add user form: {form_response.status_code}")
                return False
            
            # Extract NEW wimToken from form
            match = re.search(r'name="wimToken"\s+value="(\d+)"', form_response.text)
            if not match:
                logger.error("✗ Cannot find wimToken in add user form")
                with open('add_user_form_debug.html', 'w', encoding='utf-8') as f:
                    f.write(form_response.text)
                logger.debug("Form saved to: add_user_form_debug.html")
                return False
            
            wim_token = match.group(1)
            logger.info(f"✅ wimToken FRESCO del formulario obtenido: {wim_token}")
            
            # Extract the entryIndexIn that the printer assigned automatically
            index_match = re.search(r'name="entryIndexIn"\s+value="(\d{5})"', form_response.text)
            if index_match:
                entry_index = index_match.group(1)
                logger.info(f"✅ Índice asignado por la impresora: {entry_index}")
            else:
                logger.warning(f"⚠️  No se encontró entryIndexIn en el formulario, usando vacío")
                entry_index = ''
            
            logger.info(f"⚡ Paso 3: Enviando POST INMEDIATAMENTE")
            
            # Step 4: Build form data IMMEDIATELY (no delays)
            # Match EXACTLY the working browser request with ALL fields
            funciones = user_config.get('funciones_disponibles', {})
            available_funcs = []
            
            if funciones.get('copiadora'):
                available_funcs.append('COPY')
            if funciones.get('escaner'):
                available_funcs.append('SCAN')
            if funciones.get('impresora'):
                available_funcs.append('PRT')
            if funciones.get('document_server'):
                available_funcs.append('DOC_SERVER')
            if funciones.get('fax'):
                available_funcs.append('FAX')
            if funciones.get('navegador'):
                available_funcs.append('BROWSER')
            
            carpeta_smb = user_config.get('carpeta_smb', {})
            network_password = user_config.get('contrasena_inicio_sesion', '')
            
            # Build form data matching EXACTLY the working browser request
            # Use the entryIndexIn that the printer assigned in the form
            form_data = [
                ('inputSpecifyModeIn', 'WRITE'),
                ('listUpdateIn', 'UPDATE'),
                ('wimToken', wim_token),
                ('mode', 'ADDUSER'),
                ('pageSpecifiedIn', ''),
                ('pageNumberIn', ''),
                ('outputSpecifyModeIn', ''),
                ('inputSpecifyModeIn', ''),
                ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
                ('wayTo', 'adrsList.cgi'),
                ('isSelfPasswordEditMode', 'false'),
                ('isLocalAuthPasswordUpdated', 'false'),
                ('isFolderAuthPasswordUpdated', 'false'),  # Always false when no password
                ('entryIndexIn', entry_index),  # Use the index assigned by the printer
                ('entryNameIn', user_config.get('nombre', '')),
                ('entryDisplayNameIn', user_config.get('nombre', '')),
                ('priorityIn', '5'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('userCodeIn', user_config.get('codigo_de_usuario', '')),
                ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
                ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
                ('folderAuthUserNameIn', user_config.get('nombre_usuario_inicio_sesion', '')),
                ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
            ]
            
            # Add available functions
            for func in available_funcs:
                form_data.append(('availableFuncIn', func))
            
            # Continue with remaining fields (NO empty fields!)
            form_data.extend([
                ('entryUseIn', 'ENTRYUSE_TO_O'),
                ('entryUseIn', 'ENTRYUSE_FROM_O'),
                ('isCertificateExist', 'false'),
                ('isEncryptAlways', 'false'),
                ('folderProtocolIn', 'SMB_O'),
                ('folderPathNameIn', carpeta_smb.get('ruta', '')),
            ])
            
            # Only add password fields if password is provided
            if network_password:
                form_data.append(('folderAuthPasswordIn', network_password))
                form_data.append(('folderAuthPasswordConfirmIn', network_password))
            
            # Step 5: Send POST IMMEDIATELY (no delays!)
            url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"
            logger.info(f"📤 Enviando datos de usuario a {url}")
            
            # Add required headers (XMLHttpRequest is important!)
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'http://{printer_ip}/web/entry/es/address/adrsList.cgi'
            }
            
            response = self.session.post(
                url,
                data=form_data,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response size: {len(response.text)} characters")
            
            # Save response for debugging
            with open('provision_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.debug(f"Response saved to: provision_response.html")
            
            # Check for timeout error in response
            if 'Tiempo de sesión agotado' in response.text or 'TIMEOUT' in response.text:
                logger.error(f"✗ Session timeout error")
                return False
            
            # Check for BUSY error
            if 'BUSY' in response.text or 'está siendo utilizado' in response.text:
                logger.error(f"✗ Printer is BUSY - device is being used by other functions")
                logger.error(f"   Please wait and try again later")
                return "BUSY"
            
            # Check for other errors
            if 'Error' in response.text or 'error' in response.text:
                logger.warning(f"⚠️  Response contains 'Error' - check provision_response.html")
            
            if response.status_code in [200, 302]:
                logger.info(f"✅ User provisioned successfully to {printer_ip}")
                logger.info(f"   Response status: {response.status_code}")
                return True
            else:
                logger.error(f"✗ Provisioning failed, status: {response.status_code}")
                logger.error(f"   Response: {response.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"✗ Connection timeout to printer at {printer_ip}")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"✗ Cannot connect to printer at {printer_ip}")
            return False
        except Exception as e:
            logger.error(f"✗ Error provisioning user to {printer_ip}: {e}")
            return False
    
    def test_connection(self, printer_ip: str) -> bool:
        """
        Test if printer web interface is accessible
        
        Args:
            printer_ip: Printer IP address
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            response = self.session.get(
                f"http://{printer_ip}",
                timeout=self.timeout
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
_ricoh_web_client: Optional[RicohWebClient] = None


def get_ricoh_web_client() -> RicohWebClient:
    """
    Get or create singleton Ricoh web client instance
    
    Returns:
        RicohWebClient instance
    """
    global _ricoh_web_client
    if _ricoh_web_client is None:
        _ricoh_web_client = RicohWebClient()
    return _ricoh_web_client
