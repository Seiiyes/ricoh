"""
Ricoh Web Interface Client
Sends user configuration to Ricoh printers via HTTP/Web interface
"""
import requests
from typing import Dict, Optional
import logging
from bs4 import BeautifulSoup
import base64
import os
import time
import re
import time
import concurrent.futures
from typing import List, Tuple

logger = logging.getLogger(__name__)


class RicohWebClient:
    """
    Client for provisioning users to Ricoh printers via web interface
    """
    
    def __init__(self, timeout: int = 30, admin_user: str = "admin", admin_password: str = None):
        """
        Initialize Ricoh web client
        
        Args:
            timeout: Request timeout in seconds
            admin_user: Administrator username (default: "admin")
            admin_password: Administrator password (required, can be set via RICOH_ADMIN_PASSWORD env var)
        """
        self.timeout = timeout
        self.admin_user = admin_user
        
        # Try to get password from parameter or environment variable
        if admin_password is None:
            admin_password = os.getenv("RICOH_ADMIN_PASSWORD")
        
        # Validate that password is provided and not empty
        if not admin_password:
            raise ValueError(
                "RICOH_ADMIN_PASSWORD must be set. "
                "Configure it in environment variables or pass it explicitly."
            )
        
        self.admin_password = admin_password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        })
        # Disable SSL verification for self-signed certificates
        self.session.verify = False
        # Store authenticated sessions per printer IP
        self._authenticated_printers = set()
        self._wim_tokens = {}  # Map printer_ip to current wimToken
    
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

    def _refresh_wim_token(self, printer_ip: str) -> str:
        """
        Visita la lista de direcciones para obtener un wimToken fresco.
        Esto es crítico para evitar el error BADFLOW.
        """
        try:
            list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            logger.debug(f"Refreshing wimToken from {list_url}")
            
            # Referer es vital para engañar al equipo
            headers = {
                'Referer': f'http://{printer_ip}/web/guest/es/websys/webArch/mainFrame.cgi'
            }
            
            response = self.session.get(list_url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                match = re.search(r'name="wimToken"\s+value="(\d+)"', response.text)
                if match:
                    token = match.group(1)
                    self._wim_tokens[printer_ip] = token
                    # Mask token to show only first 4 and last 4 characters
                    token_preview = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else token
                    logger.debug(f"✅ Nuevo wimToken obtenido: {token_preview}")
                    return token
            
            logger.warning(f"⚠️  No se pudo refrescar wimToken para {printer_ip} (Status {response.status_code})")
            return self._wim_tokens.get(printer_ip, "")
        except Exception as e:
            logger.error(f"❌ Error refrescando wimToken: {e}")
            return self._wim_tokens.get(printer_ip, "")

    def _warmup_entry_session(self, printer_ip: str, entry_index: str) -> bool:
        """
        Llama al endpoint AJAX para asegurar que la entrada esté en el cache de la sesión del equipo.
        Ayuda a evitar errores BADFLOW.
        """
        try:
            ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
            wim_token = self._wim_tokens.get(printer_ip, "")
            
            # Determinar el batch (10 entradas por batch)
            try:
                batch = (int(entry_index) // 10) + 1
            except:
                batch = 1
                
            data = {
                'wimToken': wim_token,
                'loadBatch': str(batch)
            }
            headers = {
                'Referer': f'http://{printer_ip}/web/entry/es/address/adrsList.cgi',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            logger.debug(f"🔥 Warming up session for entry {entry_index} (Batch {batch})...")
            self.session.post(ajax_url, data=data, headers=headers, timeout=self.timeout)
            return True
        except Exception as e:
            logger.debug(f"Warmup falló: {e}")
            return False
    
    def _authenticate(self, printer_ip: str) -> bool:
        """
        Authenticate with the printer's web interface
        """
        if printer_ip in self._authenticated_printers:
            return True
            
        logger.info(f"🔒 Autenticando con impresora {printer_ip}...")
        
        try:
            # 1. Intentar acceder a la lista para ver si ya estamos logueados
            test_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            test_response = self.session.get(test_url, timeout=self.timeout, allow_redirects=False)
            
            # Si recibimos 200 y el token, ya estamos dentro
            if test_response.status_code == 200 and 'wimToken' in test_response.text:
                logger.debug("Sesión ya activa")
                self._authenticated_printers.add(printer_ip)
                match = re.search(r'name="wimToken"\s+value="(\d+)"', test_response.text)
                if match:
                    self._wim_tokens[printer_ip] = match.group(1)
                return True
            
            # 2. Si nos redirige o devuelve algo diferente, ir a login
            logger.info(f"🔑 Realizando login con usuario: {self.admin_user}")
            
            # Necesitamos un wimToken del formulario de login
            login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
            form_response = self.session.get(login_form_url, timeout=self.timeout)
            
            token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_response.text)
            login_token = token_match.group(1) if token_match else ""
            
            if not login_token:
                logger.error("❌ No se pudo obtener wimToken para el login")
                return False
            
            # Mask token to show only first 4 and last 4 characters
            token_preview = f"{login_token[:4]}...{login_token[-4:]}" if len(login_token) > 8 else login_token
            logger.debug(f"Login wimToken obtenido: {token_preview}")
            
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
                # Extract current wimToken for future requests
                token_match = re.search(r'name="wimToken"\s+value="(\d+)"', verify_response.text)
                if token_match:
                    self._wim_tokens[printer_ip] = token_match.group(1)
                
                self._authenticated_printers.add(printer_ip)
                return True
            
            logger.error(f"❌ Autenticación fallida")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error durante autenticación: {e}")
            return False
    
    def provision_user(self, printer_ip: str, user_config: Dict):
        """
        Provision a user to a Ricoh printer via web interface
        
        Args:
            printer_ip: Printer IP address
            user_config: User configuration dictionary
        
        Returns:
            True if successful
            "BUSY" if printer is busy
            "BADFLOW" if anti-scraping protection triggered
            "TIMEOUT" if connection timeout
            "CONNECTION" if connection error
            False for other errors
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
            # Mask token to show only first 4 and last 4 characters
            token_preview = f"{list_wim_token[:4]}...{list_wim_token[-4:]}" if len(list_wim_token) > 8 else list_wim_token
            logger.info(f"✅ wimToken de lista obtenido: {token_preview}")
            
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
            # Mask token to show only first 4 and last 4 characters
            token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
            logger.info(f"✅ wimToken FRESCO del formulario obtenido: {token_preview}")
            
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
            
            # Si no hay contraseña, usar "Temporal2021" por defecto
            if not network_password:
                network_password = 'Temporal2021'
                logger.info(f"⚠️  No se proporcionó contraseña, usando 'Temporal2021' por defecto")
            
            # Determinar si se debe marcar como actualizada la contraseña
            is_password_updated = 'true' if network_password else 'false'
            
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
                ('isFolderAuthPasswordUpdated', is_password_updated),  # true si hay contraseña
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
            
            # Always add password fields (using Temporal2021 if not provided)
            form_data.append(('folderAuthPasswordIn', network_password))
            form_data.append(('folderAuthPasswordConfirmIn', network_password))
            
            logger.info(f"🔐 Contraseña de carpeta configurada: {'***' if network_password else '(vacía)'}")
            
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
            
            # Check for BADFLOW error (anti-scraping protection)
            if 'BADFLOW' in response.text:
                logger.error(f"✗ BADFLOW detected - Printer rejected the request flow")
                logger.error(f"   Usually happens when cookies or wimToken are invalid or session expired")
                return "BADFLOW"
            
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
            return "TIMEOUT"
        except requests.exceptions.ConnectionError:
            logger.error(f"✗ Cannot connect to printer at {printer_ip}")
            return "CONNECTION"
        except Exception as e:
            logger.error(f"✗ Error provisioning user to {printer_ip}: {e}")
            return False
    
    def reset_session(self):
        """
        Reset the session and authenticated printers cache
        Useful when switching between different printers
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        })
        self.session.verify = False
        self._authenticated_printers = set()
        self._wim_tokens = {}  # Limpiar tokens cacheados
        logger.debug("Session reset - cleared cookies and tokens")
    
    
    def find_specific_user(self, printer_ip: str, user_code: str) -> Optional[Dict]:
        """
        Busca un usuario específico en una impresora por su código.
        """
        logger.info(f"🔍 Buscando usuario {user_code} en {printer_ip}...")
        
        try:
            # 1. Leer solo la lista básica (Rápido)
            all_users = self.read_users_from_printer(printer_ip, fast_list=True)
            
            logger.info(f"   Total usuarios en impresora: {len(all_users)}")
            
            # 2. Buscar el usuario específico (comparación flexible)
            target_user = None
            user_code_str = str(user_code).strip()
            
            for user in all_users:
                codigo_impresora = str(user.get('codigo', '')).strip()
                logger.debug(f"   Comparando: '{codigo_impresora}' vs '{user_code_str}'")
                
                if codigo_impresora == user_code_str:
                    target_user = user
                    break
            
            if not target_user:
                logger.warning(f"❌ Usuario {user_code} no encontrado en {printer_ip}")
                logger.info(f"   Usuarios disponibles (primeros 5):")
                for i, user in enumerate(all_users[:5]):
                    logger.info(f"     {i+1}. Código: '{user.get('codigo')}', Nombre: '{user.get('nombre')}'")
                return None
            
            logger.info(f"✅ Usuario {user_code} encontrado: {target_user.get('nombre')} (entry_index: {target_user.get('entry_index')})")
            
            # 3. Solo ahora pedimos los detalles (permisos, carpeta) de ESTE usuario
            details = self._get_user_details(printer_ip, target_user['entry_index'])
            
            if not details:
                logger.error(f"❌ No se pudieron recuperar los detalles reales del usuario {user_code}")
                return None
                
            target_user['permisos'] = details.get('permisos', {})
            target_user['carpeta'] = details.get('carpeta', '')
            target_user['lazy'] = False
            
            logger.info(f"   Permisos obtenidos: {target_user['permisos']}")
            
            return target_user
                
        except Exception as e:
            logger.error(f"❌ Error buscando usuario: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def read_users_from_printer(self, printer_ip: str, fast_list: bool = False) -> list:
        """
        Lee todos los usuarios de una impresora usando el endpoint AJAX original de Ricoh
        
        Args:
            printer_ip: IP de la impresora
            fast_list: Si es True, no descarga los detalles (permisos) de cada usuario.
                       Ideal para vistas de lista rápidas (Lazy Loading).
        """
        logger.info(f"📋 Leyendo usuarios de {printer_ip} vía AJAX (CGI)... {'(Modo Rápido)' if fast_list else ''}")
        
        try:
            # 1. Autenticar
            if not self._authenticate(printer_ip):
                logger.error(f"❌ No se pudo autenticar con {printer_ip}")
                return []
            
            all_users = []
            ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'http://{printer_ip}/web/entry/es/address/adrsList.cgi'
            }
            
            # 2. Consultar lotes de 50 usuarios
            for batch in range(1, 25):
                logger.debug(f"   Solicitando lote {batch} de usuarios...")
                payload = {
                    'listCountIn': '50',
                    'getCountIn': str(batch)
                }
                
                try:
                    response = self.session.post(
                        ajax_url, 
                        data=payload, 
                        headers=headers, 
                        timeout=self.timeout
                    )
                    
                    logger.debug(f"      Batch {batch} status: {response.status_code}, Length: {len(response.text)}")
                    
                    if response.status_code != 200 or not response.text.strip():
                        break
                    
                    responseText = response.text.strip()
                    if batch == 1:
                        logger.debug(f"   [DEBUG] Batch 1 sample: {responseText[:200]}...")
                    
                    import ast
                    import json
                    # Ricoh responses often use single quotes, which json.loads hates but literal_eval loves
                    try:
                        data = ast.literal_eval(responseText)
                    except (ValueError, SyntaxError):
                        # Fallback to json.loads after replacing single quotes
                        data = json.loads(responseText.replace("'", '"'))
                        
                    for entry in data:
                        if len(entry) >= 5:
                            # Detectar formato basado en si el primer elemento es string vacío
                            # .253 format: ['',1,'00001','YESICA GARCIA',1,'AB','','','1717',...]
                            # .252 format: [231,1,'00001','YESICA GARCIA','1717',...]
                            
                            if entry[0] == '' and len(entry) >= 9:
                                # Formato .253 (con campo vacío al inicio)
                                idx = str(entry[2])      # entry_index
                                name = str(entry[3])     # nombre
                                code = str(entry[8])     # código real está más adelante
                                folder = str(entry[11]) if len(entry) >= 12 else ""
                            else:
                                # Formato .252 (formato estándar)
                                idx = str(entry[2])
                                name = str(entry[3])
                                code = str(entry[4])
                                folder = str(entry[7]) if len(entry) >= 8 else ""
                            
                            # Debug: mostrar primeros 3 usuarios del primer batch
                            if batch == 1 and len(all_users) < 3:
                                logger.debug(f"      Usuario {len(all_users)+1}: idx={idx}, name={name}, code={code}, folder={folder}")
                            
                            all_users.append((idx, name, code, folder))
                    
                    logger.debug(f"      Parsed {len(data)} entries from batch {batch}")
                except Exception as parse_error:
                    logger.debug(f"      Parse error on batch {batch}: {parse_error}. Trying regex fallback...")
                    # Revised regex to capture more reliably
                    pattern = r"\[\d+,\d+,'([^']*)','([^']*)','([^']*)'(?:,'[^']*')?(?:,'[^']*')?(?:,'([^']*)')?"
                    matches = re.findall(pattern, responseText)
                    if matches:
                        for match in matches:
                            idx, name, code, folder = match
                            all_users.append((idx, name, code, folder if folder else ""))
                        logger.debug(f"      Regex found {len(matches)} matches in batch {batch}")
                    else:
                        logger.warning(f"      No users found in batch {batch} response")
                         
                except Exception as batch_error:
                    logger.error(f"   Error en lote {batch}: {batch_error}")
                    break
            
            logger.info(f"   Total de {len(all_users)} usuarios encontrados antes de filtrar duplicados.")
            # 3. Procesar lista única
            unique_user_data = []
            seen_indices = set()
            
            for entry_index, nombre, codigo, carpeta_ajax in all_users:
                if entry_index in seen_indices: continue
                seen_indices.add(entry_index)
                
                # Limpiar espacios
                nombre = nombre.strip() if nombre else ""
                codigo = codigo.strip() if codigo else ""
                
                # Si el código está vacío o no es numérico, intentar intercambiar con nombre
                if not codigo or not codigo.isdigit():
                    if nombre and nombre.isdigit():
                        # Intercambiar: el nombre es el código y viceversa
                        nombre, codigo = codigo, nombre
                        logger.debug(f"   Intercambiado nombre/código para entry {entry_index}: código={codigo}, nombre={nombre}")
                
                # Si después del intercambio el código sigue sin ser numérico, intentar extraer números
                if not codigo or not codigo.isdigit():
                    # Intentar extraer solo los dígitos del código
                    import re
                    digits = re.sub(r'\D', '', codigo)
                    if digits:
                        codigo = digits
                        logger.debug(f"   Extraídos dígitos del código para entry {entry_index}: {codigo}")
                    else:
                        # Si definitivamente no hay código numérico, saltar este usuario
                        logger.debug(f"   Saltando entry {entry_index}: no se pudo obtener código numérico (nombre={nombre}, codigo_original={codigo})")
                        continue
                
                unique_user_data.append((nombre, codigo, entry_index, carpeta_ajax))

            # Permisos vacíos por defecto - se llenan al leer desde la impresora
            empty_permissions = {
                'copiadora': False, 'escaner': False, 'impresora': False,
                'document_server': False, 'fax': False, 'navegador': False
            }

            # 4. Obtener detalles si no es fast_list
            final_users = []
            
            if fast_list:
                logger.info(f"✅ Lista básica obtenida: {len(unique_user_data)} usuarios (Saltando detalles)")
                for u_nombre, u_codigo, u_index, u_carpeta_ajax in unique_user_data:
                    final_users.append({
                        'nombre': u_nombre,
                        'codigo': u_codigo,
                        'entry_index': u_index,
                        'empresa': '',
                        'permisos': empty_permissions.copy(),
                        'carpeta': u_carpeta_ajax,
                        'lazy': True
                    })
                return final_users

            logger.info(f"   Iniciando lectura de funciones para {len(unique_user_data)} usuarios (Modo Secuencial para evitar BADFLOW)...")
            
            # USO SECUENCIAL: Ricoh no soporta múltiples flujos concurrentes en la misma sesión (causa BADFLOW)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future_to_user = {
                    executor.submit(self._get_user_details, printer_ip, u[2], fast_sync=True): u 
                    for u in unique_user_data
                }
                
                count = 0
                for future in concurrent.futures.as_completed(future_to_user):
                    u_nombre, u_codigo, u_index, u_carpeta_ajax = future_to_user[future]
                    try:
                        user_details = future.result()
                        final_users.append({
                            'nombre': u_nombre,
                            'codigo': u_codigo,
                            'entry_index': u_index,
                            'empresa': '',
                            'permisos': user_details.get('permisos', {}) if user_details else empty_permissions.copy(),
                            'carpeta': u_carpeta_ajax or (user_details.get('carpeta', '') if user_details else ''),
                            'lazy': False
                        })
                    except Exception as exc:
                        logger.error(f"   Error procesando user {u_codigo}: {exc}")
                    
                    count += 1
                    if count % 50 == 0:
                        logger.info(f"   ... {count}/{len(unique_user_data)} usuarios procesados")
            
            logger.info(f"✅ Sincronización completa: {len(final_users)} usuarios leídos de {printer_ip}")
            return final_users
        except Exception as e:
            logger.error(f"❌ Error leyendo usuarios vía AJAX: {e}")
            return []
    
    def _get_user_details(self, printer_ip: str, entry_index: str, fast_sync: bool = False) -> Optional[Dict]:
        """
        Lee los detalles de un usuario específico, incluyendo funciones disponibles
        OPTIMIZADO: Usa el flujo correcto descubierto mediante reverse engineering
        
        Args:
            printer_ip: IP de la impresora
            entry_index: Índice del usuario
            fast_sync: Si es True, no usa Selenium para ser más rápido
            
        Returns:
            Dict con detalles del usuario o None
        """
        logger.debug(f"📋 Detalles de usuario {entry_index}")
        
        # NO usar permisos por defecto - si no se pueden leer, devolver None
        # Esto fuerza al frontend a mostrar un error en lugar de datos incorrectos
        
        # Intentar con requests usando el flujo correcto (RÁPIDO)
        try:
            # 1. Asegurar que tenemos wimToken fresco
            list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            list_resp = self.session.get(list_url, timeout=self.timeout)
            
            wim_token = ""
            match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
            if match:
                wim_token = match.group(1)
                self._wim_tokens[printer_ip] = wim_token
            else:
                wim_token = self._wim_tokens.get(printer_ip, "")

            # 2. Cargar el batch que contiene este usuario (CRÍTICO para evitar BADFLOW)
            ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
            batch = (int(entry_index) // 50) + 1
            
            ajax_data = {
                'wimToken': wim_token,
                'listCountIn': '50',
                'getCountIn': str(batch)
            }
            
            ajax_headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': list_url,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            self.session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=self.timeout)
            
            # 3. Solicitar formulario con el flujo correcto (descubierto en JavaScript)
            edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
            
            # CLAVE: Usar MODUSER y PROGRAMMED (no EDIT y DEFAULT)
            form_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',  # Como lo hace el JavaScript
                'outputSpecifyModeIn': 'PROGRAMMED',  # Como lo hace el JavaScript
                'entryIndexIn': entry_index
            }
            
            headers = {
                'Referer': list_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            logger.debug(f"🔍 POST details con MODUSER/PROGRAMMED: {entry_index}")
            response = self.session.post(edit_url, data=form_data, headers=headers, timeout=self.timeout)
            
            # Verificar si hay redirección a login (sesión expirada)
            if "authForm.cgi" in response.text or response.status_code == 302:
                logger.warning(f"⚠️  Sesión expirada, re-autenticando...")
                # Re-autenticar
                if not self._authenticate(printer_ip):
                    logger.error(f"❌ No se pudo re-autenticar")
                    return None
                
                # Reintentar después de autenticar - FLUJO COMPLETO
                list_resp = self.session.get(list_url, timeout=self.timeout)
                match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
                if match:
                    wim_token = match.group(1)
                    form_data['wimToken'] = wim_token
                    ajax_data['wimToken'] = wim_token  # Actualizar también en ajax_data
                
                # Recargar el batch con el nuevo token
                self.session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=self.timeout)
                response = self.session.post(edit_url, data=form_data, headers=headers, timeout=self.timeout)
            
            # Verificar si hay BADFLOW (no debería haberlo con este flujo)
            if "BADFLOW" in response.text:
                logger.warning(f"⚠️  BADFLOW inesperado con flujo correcto")
                return None
            
            if response.status_code != 200:
                logger.warning(f"⚠️  HTTP falló (Status {response.status_code})")
                return None
            
            # Parsear HTML para extraer funciones
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Inicializar permisos vacíos
            permisos = {
                'copiadora': False, 'copiadora_color': False,
                'impresora': False, 'impresora_color': False,
                'escaner': False, 'document_server': False,
                'fax': False, 'navegador': False
            }
            
            # Buscar checkboxes de funciones disponibles
            checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})
            
            # Si no encontramos checkboxes, puede ser error temporal - reintentar
            if not checkboxes:
                logger.warning(f"⚠️  No se encontraron checkboxes en primer intento, reintentando...")
                
                # Verificar si es una redirección (sesión expirada)
                if "authForm.cgi" in response.text or "<form name='form1'" in response.text:
                    logger.warning(f"⚠️  Detectada redirección a login, re-autenticando...")
                    if not self._authenticate(printer_ip):
                        logger.error(f"❌ No se pudo re-autenticar")
                        return None
                
                time.sleep(2)
                
                # Reintentar todo el flujo con token fresco
                list_resp = self.session.get(list_url, timeout=self.timeout)
                match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
                if match:
                    wim_token = match.group(1)
                    ajax_data['wimToken'] = wim_token
                    form_data['wimToken'] = wim_token
                
                self.session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=self.timeout)
                response = self.session.post(edit_url, data=form_data, headers=headers, timeout=self.timeout)
                soup = BeautifulSoup(response.text, 'html.parser')
                checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})
                
                if checkboxes:
                    logger.info(f"   ✅ Checkboxes encontrados en segundo intento")
            
            if checkboxes:
                # Log de TODOS los checkboxes encontrados para debug
                logger.debug(f"   📋 Total checkboxes encontrados: {len(checkboxes)}")
                for i, cb in enumerate(checkboxes, 1):
                    val = cb.get('value', '')
                    # Verificar diferentes formas de "checked"
                    is_checked = (
                        cb.has_attr('checked') or 
                        cb.get('checked') == 'checked' or 
                        cb.get('checked') == 'true' or
                        cb.get('checked') == '1'
                    )
                    checked_str = '✅' if is_checked else '❌'
                    # Mostrar todos los atributos del checkbox para debug
                    attrs = {k: v for k, v in cb.attrs.items() if k != 'type'}
                    logger.debug(f"      {checked_str} {i}. value='{val}' attrs={attrs}")
                
                # Si encontramos checkboxes, marcar solo los que tienen 'checked'
                for checkbox in checkboxes:
                    val = checkbox.get('value', '').upper()
                    # Verificar diferentes formas de "checked"
                    is_checked = (
                        checkbox.has_attr('checked') or 
                        checkbox.get('checked') == 'checked' or 
                        checkbox.get('checked') == 'true' or
                        checkbox.get('checked') == '1'
                    )
                    
                    if is_checked:
                        # Mapeo de valores reales de Ricoh
                        if 'COPY' in val:
                            if any(x in val for x in ['FC', 'FULL']):
                                permisos['copiadora_color'] = True
                            elif any(x in val for x in ['BW', 'TC', 'MC']):
                                permisos['copiadora'] = True
                            elif val == 'COPY':  # Valor simple sin sufijo
                                permisos['copiadora'] = True
                        elif 'PRT' in val or 'PRINT' in val:
                            if any(x in val for x in ['FC', 'FULL']):
                                permisos['impresora_color'] = True
                            elif 'BW' in val:
                                permisos['impresora'] = True
                            elif val == 'PRT' or val == 'PRINT':  # Valor simple sin sufijo
                                permisos['impresora'] = True
                        elif 'SCAN' in val:
                            permisos['escaner'] = True
                        elif any(x in val for x in ['DBX', 'DOC_SERVER', 'DOCSERVER', 'DOC']):
                            permisos['document_server'] = True
                        elif 'FAX' in val:
                            permisos['fax'] = True
                        elif 'BROWSER' in val or 'MFPBROWSER' in val:
                            permisos['navegador'] = True
                
                logger.debug(f"   ✅ Permisos leídos del hardware: {permisos}")
            else:
                logger.error(f"❌ No se encontraron checkboxes en el HTML")
                # Guardar HTML para debug
                debug_file = f"/tmp/debug_no_checkboxes_{entry_index}.html"
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.error(f"   HTML guardado en: {debug_file}")
                except:
                    pass
                # NO usar defaults - devolver None para indicar error
                return None
            
            # Extraer wimToken
            wim_token = ''
            token_input = soup.find('input', {'name': 'wimToken'})
            if token_input:
                wim_token = token_input.get('value', '')
            
            # Extraer carpeta SMB
            carpeta = ''
            carpeta_input = soup.find('input', {'name': 'folderPathNameIn'})
            if carpeta_input:
                carpeta = carpeta_input.get('value', '')
            
            return {
                'permisos': permisos,
                'carpeta': carpeta,
                '_new_token': wim_token
            }
            
        except Exception as e:
            logger.error(f"❌ Error leyendo detalles: {e}")
            return None

    def set_user_functions(self, printer_ip: str, entry_index: str, permissions: Dict) -> bool:
            """
            Actualiza las funciones de un usuario en la impresora.
            Usa el flujo correcto descubierto mediante reverse engineering.
            """
            try:
                logger.info(f"Actualizando funciones: Usuario {entry_index} en {printer_ip}")

                if not self._authenticate(printer_ip):
                    logger.error(f"Fallo autenticacion con {printer_ip}")
                    return False

                # 1. Obtener wimToken fresco
                list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
                list_resp = self.session.get(list_url, timeout=self.timeout)

                wim_token = ""
                match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
                if match:
                    wim_token = match.group(1)
                    self._wim_tokens[printer_ip] = wim_token

                # 2. Cargar batch AJAX (CRÍTICO)
                ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
                batch = (int(entry_index) // 50) + 1

                ajax_data = {
                    'wimToken': wim_token,
                    'listCountIn': '50',
                    'getCountIn': str(batch)
                }

                ajax_headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': list_url,
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

                self.session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=self.timeout)

                # 3. Obtener formulario con flujo correcto
                edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"

                # USAR FLUJO CORRECTO: MODUSER + PROGRAMMED para leer
                form_data = {
                    'wimToken': wim_token,
                    'mode': 'MODUSER',
                    'outputSpecifyModeIn': 'PROGRAMMED',
                    'inputSpecifyModeIn': 'READ',
                    'entryIndexIn': entry_index
                }

                headers = {
                    'Referer': list_url,
                    'Content-Type': 'application/x-www-form-urlencoded',
                }

                logger.info(f"   Obteniendo formulario...")
                response = self.session.post(edit_url, data=form_data, headers=headers, timeout=self.timeout)

                if response.status_code != 200:
                    logger.error(f"Error al leer formulario: Status {response.status_code}")
                    return False

                if "BADFLOW" in response.text:
                    logger.warning("BADFLOW detectado, usando Selenium...")
                    try:
                        from services.ricoh_selenium_client import get_selenium_client
                        selenium_client = get_selenium_client()

                        return selenium_client.set_user_permissions(
                            printer_ip,
                            entry_index,
                            permissions,
                            self.admin_user,
                            self.admin_password,
                            http_session=self.session
                        )
                    except Exception as sel_err:
                        logger.error(f"Fallo Selenium: {sel_err}")
                        return False

                soup = BeautifulSoup(response.text, 'html.parser')

                # Obtener nuevo wimToken del formulario
                token_input = soup.find('input', {'name': 'wimToken'})
                if token_input:
                    wim_token = token_input.get('value', wim_token)

                # 4. Leer funciones actuales de los checkboxes
                html_checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})

                if not html_checkboxes:
                    logger.error("No se encontraron checkboxes de funciones")
                    return False

                logger.info(f"   {len(html_checkboxes)} checkboxes encontrados")
                
                # Log de TODOS los checkboxes disponibles
                all_checkbox_values = [cb.get('value', '') for cb in html_checkboxes]
                logger.info(f"   Checkboxes disponibles: {all_checkbox_values}")
                
                logger.info(f"   Permisos solicitados: {permissions}")

                # 5. Determinar qué funciones activar según permisos solicitados
                active_funcs = []
                excluded_funcs = []
                for cb in html_checkboxes:
                    val = cb.get('value', '').upper()
                    is_needed = False

                    # Mapeo basado en valores reales de Ricoh
                    if 'COPY' in val:
                        # FC = Full Color (A todo color)
                        # TC = Two Colors (Dos colores) 
                        # MC = Multi Color (Color personalizado)
                        # BW = Black & White (Blanco y negro)
                        if any(x in val for x in ['FC', 'FULL', 'COLOR', 'TC', 'MC']):
                            # Solo incluir funciones de color si copiadora_color está habilitado
                            if permissions.get('copiadora_color'):
                                is_needed = True
                            # Si copiadora_color=False, explícitamente NO incluir (is_needed queda False)
                        elif 'BW' in val:
                            # Incluir funciones B/N si copiadora está habilitado
                            if permissions.get('copiadora'):
                                is_needed = True
                    elif 'PRT' in val or 'PRINT' in val:
                        if any(x in val for x in ['FC', 'FULL', 'COLOR']):
                            # Solo incluir funciones de color si impresora_color está habilitado
                            if permissions.get('impresora_color'):
                                is_needed = True
                            # Si impresora_color=False, explícitamente NO incluir (is_needed queda False)
                        elif 'BW' in val:
                            # Incluir funciones B/N si impresora está habilitado
                            if permissions.get('impresora'):
                                is_needed = True
                    elif 'SCAN' in val:
                        if permissions.get('escaner'): is_needed = True
                    elif any(x in val for x in ['DBX', 'DOC_SERVER', 'DOCSERVER']):
                        if permissions.get('document_server'): is_needed = True
                    elif 'FAX' in val:
                        if permissions.get('fax'): is_needed = True
                    elif 'BROWSER' in val or 'MFPBROWSER' in val:
                        if permissions.get('navegador'): is_needed = True

                    if is_needed:
                        active_funcs.append(cb.get('value'))
                    else:
                        # Registrar funciones que se están excluyendo explícitamente
                        if 'COPY' in val or 'PRT' in val or 'PRINT' in val:
                            excluded_funcs.append(cb.get('value'))

                logger.info(f"   Funciones a ACTIVAR ({len(active_funcs)}): {active_funcs}")
                logger.info(f"   Funciones a DESACTIVAR ({len(excluded_funcs)}): {excluded_funcs}")

                # 6. Obtener información del usuario para campos obligatorios
                user_name_input = soup.find('input', {'name': 'entryNameIn'})
                user_code_input = soup.find('input', {'name': 'userCodeIn'})

                user_name = user_name_input.get('value', '') if user_name_input else ''
                user_code = user_code_input.get('value', '') if user_code_input else ''

                # 7. Construir payload con TODOS los campos obligatorios
                # Estos son los campos mínimos que Ricoh requiere para actualizar
                payload = [
                    ('wimToken', wim_token),
                    ('mode', 'MODUSER'),
                    ('inputSpecifyModeIn', 'WRITE'),
                    ('listUpdateIn', 'UPDATE'),
                    ('entryIndexIn', entry_index),
                    ('entryNameIn', user_name),
                    ('entryDisplayNameIn', user_name),
                    ('userCodeIn', user_code),
                    ('priorityIn', '5'),
                    ('outputSpecifyModeIn', ''),
                    ('pageSpecifiedIn', ''),
                    ('pageNumberIn', ''),
                    ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
                    ('wayTo', 'adrsList.cgi'),
                    ('isSelfPasswordEditMode', 'false'),
                    ('isLocalAuthPasswordUpdated', 'false'),
                    ('isFolderAuthPasswordUpdated', 'false'),
                    ('entryTagInfoIn', '1'),
                    ('entryTagInfoIn', '1'),
                    ('entryTagInfoIn', '1'),
                    ('entryTagInfoIn', '1'),
                    ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
                    ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
                    ('folderAuthUserNameIn', ''),
                    ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
                    ('entryUseIn', 'ENTRYUSE_TO_O'),
                    ('entryUseIn', 'ENTRYUSE_FROM_O'),
                    ('isCertificateExist', 'false'),
                    ('isEncryptAlways', 'false'),
                    ('folderProtocolIn', 'SMB_O'),
                    ('folderPathNameIn', '\\\\TIC-0122\\Escaner'),
                ]

                # Agregar funciones seleccionadas
                for func in active_funcs:
                    payload.append(('availableFuncIn', func))

                logger.info(f"   Enviando: {len(payload)} campos + {len(active_funcs)} funciones")

                # 8. Enviar actualización
                update_url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"
                update_headers = { 
                    'Referer': edit_url,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

                resp = self.session.post(update_url, data=payload, headers=update_headers, timeout=self.timeout)

                logger.info(f"   Respuesta: Status {resp.status_code}")

                if resp.status_code == 200:
                    # Verificar que no haya errores en la respuesta
                    if "BADFLOW" not in resp.text and "Error" not in resp.text:
                        logger.info(f"Actualizacion exitosa en {printer_ip}")
                        return True
                    else:
                        logger.error(f"La impresora rechazo la actualizacion: {resp.text[:200]}")
                        return False

                logger.error(f"La impresora rechazo la actualizacion (Status {resp.status_code})")
                return False

            except Exception as e:
                logger.error(f"Error en set_user_functions: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return False

    def update_user_in_printer(self, printer_ip: str, user_data: Dict) -> bool:
        """
        Actualiza un usuario existente en una impresora con nuevos datos (carpeta, credenciales, permisos)
        
        IMPORTANTE: 
        - Solo actualiza campos que existen en la impresora Ricoh
        - Actualización inteligente: solo modifica los campos que vienen en user_data
        - Si no vienen permisos, LEE los actuales de la impresora y los mantiene
        - NO incluye empresa ni centro_costos (esos son solo para DB)
        
        Args:
            printer_ip: IP de la impresora
            user_data: Diccionario con los datos del usuario:
                - entry_index: ID del usuario en la impresora (REQUERIDO)
                - nombre: Nombre del usuario (opcional)
                - codigo: Código de usuario (opcional)
                - carpeta: Ruta SMB (opcional)
                - usuario_red: Usuario de red (opcional)
                - permisos: Dict con permisos (opcional - si no viene, lee y mantiene los actuales)
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        logger.info(f"🔄 Actualizando usuario {user_data.get('codigo', 'N/A')} en {printer_ip}")
        logger.info(f"   Actualización inteligente: solo campos proporcionados")
        logger.info(f"   ⚠️  empresa y centro_costos NO se sincronizan (solo existen en DB)")
        
        try:
            # 1. Autenticar
            if not self._authenticate(printer_ip):
                logger.error(f"❌ No se pudo autenticar con {printer_ip}")
                return False
            
            entry_index = user_data.get('entry_index')
            if not entry_index:
                logger.error(f"❌ No se proporcionó entry_index")
                return False
            
            # 2. Si no vienen permisos, leer los actuales de la impresora
            if 'permisos' not in user_data or not user_data['permisos']:
                logger.info(f"   🔍 Leyendo permisos actuales de la impresora...")
                try:
                    current_details = self._get_user_details(printer_ip, entry_index, fast_sync=True)
                    if current_details and 'permisos' in current_details:
                        user_data['permisos'] = current_details['permisos']
                        logger.info(f"   ✅ Permisos actuales obtenidos: {user_data['permisos']}")
                    else:
                        logger.warning(f"   ⚠️  No se pudieron leer permisos actuales, usando vacíos")
                        user_data['permisos'] = {
                            'copiadora': False,
                            'copiadora_color': False,
                            'impresora': False,
                            'impresora_color': False,
                            'escaner': False,
                            'document_server': False,
                            'fax': False,
                            'navegador': False
                        }
                except Exception as e:
                    logger.error(f"   ❌ Error leyendo permisos actuales: {e}")
                    return False
            
            # 3. Obtener wimToken de la lista
            list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            list_resp = self.session.get(list_url, timeout=self.timeout)
            
            match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
            if not match:
                logger.error(f"❌ No se pudo obtener wimToken")
                return False
            
            wim_token = match.group(1)
            # Mask token to show only first 4 and last 4 characters
            token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
            logger.debug(f"✅ wimToken obtenido: {token_preview}")
            
            # 4. Obtener el formulario de edición (modo READ para leer campos actuales)
            edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
            form_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',
                'outputSpecifyModeIn': 'PROGRAMMED',
                'inputSpecifyModeIn': 'READ',
                'entryIndexIn': entry_index
            }
            
            headers = {
                'Referer': list_url,
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            logger.info(f"   Obteniendo formulario de edición...")
            response = self.session.post(edit_url, data=form_data, headers=headers, timeout=self.timeout)
            
            if response.status_code != 200:
                logger.error(f"❌ Error al leer formulario: Status {response.status_code}")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Obtener nuevo wimToken del formulario
            token_input = soup.find('input', {'name': 'wimToken'})
            if token_input:
                wim_token = token_input.get('value', wim_token)
            
            # 5. Leer valores ACTUALES del formulario (para mantener lo que no se modifica)
            current_name_input = soup.find('input', {'name': 'entryNameIn'})
            current_code_input = soup.find('input', {'name': 'userCodeIn'})
            current_folder_input = soup.find('input', {'name': 'folderPathNameIn'})
            current_user_input = soup.find('input', {'name': 'folderAuthUserNameIn'})
            
            current_name = current_name_input.get('value', '') if current_name_input else ''
            current_code = current_code_input.get('value', '') if current_code_input else ''
            current_folder = current_folder_input.get('value', '') if current_folder_input else ''
            current_user = current_user_input.get('value', '') if current_user_input else ''
            
            # Usar valores nuevos si vienen, sino mantener los actuales
            final_name = user_data.get('nombre', current_name)
            final_code = user_data.get('codigo', current_code)
            final_folder = user_data.get('carpeta', current_folder)
            final_user = user_data.get('usuario_red', current_user)
            
            logger.info(f"   📝 Nombre: {current_name} → {final_name}")
            logger.info(f"   📝 Código: {current_code} → {final_code}")
            logger.info(f"   📝 Carpeta: {current_folder} → {final_folder}")
            logger.info(f"   📝 Usuario red: {current_user} → {final_user}")
            
            # 6. Preparar permisos usando los que ya leímos
            html_checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})
            
            permisos = user_data['permisos']
            logger.info(f"   🔧 Usando permisos: {permisos}")
            
            active_funcs = []
            for cb in html_checkboxes:
                val = cb.get('value', '').upper()
                is_needed = False
                
                # Mapeo basado en valores reales de Ricoh
                if 'COPY' in val:
                    if any(x in val for x in ['FC', 'FULL', 'COLOR']):
                        if permisos.get('copiadora_color'): is_needed = True
                    elif any(x in val for x in ['BW', 'TC', 'MC']):
                        if permisos.get('copiadora'): is_needed = True
                    elif val == 'COPY':  # Formato simple (.252)
                        if permisos.get('copiadora'): is_needed = True
                elif 'PRT' in val or 'PRINT' in val:
                    if any(x in val for x in ['FC', 'FULL', 'COLOR']):
                        if permisos.get('impresora_color'): is_needed = True
                    elif 'BW' in val:
                        if permisos.get('impresora'): is_needed = True
                    elif val == 'PRT':  # Formato simple (.252)
                        if permisos.get('impresora'): is_needed = True
                elif 'SCAN' in val:
                    if permisos.get('escaner'): is_needed = True
                elif any(x in val for x in ['DBX', 'DOC_SERVER', 'DOCSERVER']):
                    if permisos.get('document_server'): is_needed = True
                elif 'FAX' in val:
                    if permisos.get('fax'): is_needed = True
                elif 'BROWSER' in val or 'MFPBROWSER' in val:
                    if permisos.get('navegador'): is_needed = True
                
                if is_needed:
                    active_funcs.append(cb.get('value'))
            
            logger.info(f"   ✅ Funciones activas: {active_funcs}")
            
            # 7. Construir payload con TODOS los campos obligatorios
            payload = [
                ('wimToken', wim_token),
                ('mode', 'MODUSER'),
                ('inputSpecifyModeIn', 'WRITE'),
                ('listUpdateIn', 'UPDATE'),
                ('entryIndexIn', entry_index),
                ('entryNameIn', final_name),
                ('entryDisplayNameIn', final_name),
                ('userCodeIn', final_code),
                ('priorityIn', '5'),
                ('outputSpecifyModeIn', ''),
                ('pageSpecifiedIn', ''),
                ('pageNumberIn', ''),
                ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
                ('wayTo', 'adrsList.cgi'),
                ('isSelfPasswordEditMode', 'false'),
                ('isLocalAuthPasswordUpdated', 'false'),
                ('isFolderAuthPasswordUpdated', 'false'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
                ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
                ('folderAuthUserNameIn', final_user),
                ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
                ('entryUseIn', 'ENTRYUSE_TO_O'),
                ('entryUseIn', 'ENTRYUSE_FROM_O'),
                ('isCertificateExist', 'false'),
                ('isEncryptAlways', 'false'),
                ('folderProtocolIn', 'SMB_O'),
                ('folderPathNameIn', final_folder),
            ]
            
            # Agregar funciones seleccionadas
            for func in active_funcs:
                payload.append(('availableFuncIn', func))
            
            logger.info(f"   📤 Enviando: {len(payload)} campos + {len(active_funcs)} funciones")
            
            # 8. Enviar actualización
            update_url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"
            update_headers = { 
                'Referer': edit_url,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            resp = self.session.post(update_url, data=payload, headers=update_headers, timeout=self.timeout)
            
            logger.info(f"   Respuesta: Status {resp.status_code}")
            
            # Guardar respuesta para debug
            with open(f'update_user_response_{entry_index}.html', 'w', encoding='utf-8') as f:
                f.write(resp.text)
            logger.debug(f"   Respuesta guardada en: update_user_response_{entry_index}.html")
            
            if resp.status_code == 200:
                # Verificar que no haya errores en la respuesta
                if "BADFLOW" not in resp.text and "Error" not in resp.text and "error" not in resp.text.lower():
                    logger.info(f"   ✅ Usuario actualizado correctamente en {printer_ip}")
                    return True
                else:
                    logger.error(f"   ❌ La impresora rechazó la actualización")
                    logger.error(f"   Ver detalles en: update_user_response_{entry_index}.html")
                    return False
            
            logger.error(f"   ❌ Error HTTP {resp.status_code}")
            return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando usuario: {e}")
            import traceback
            logger.debug(traceback.format_exc())
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
        # Leer credenciales de admin desde variables de entorno
        admin_user = os.getenv('RICOH_ADMIN_USER', 'admin')
        admin_password = os.getenv('RICOH_ADMIN_PASSWORD', '')
        _ricoh_web_client = RicohWebClient(
            admin_user=admin_user,
            admin_password=admin_password
        )
    return _ricoh_web_client
