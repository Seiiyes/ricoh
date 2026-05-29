"""
Ricoh Password Configuration Flow
Maneja el flujo correcto para configurar contraseñas de autenticación de carpeta
"""
import requests
import logging
import re
import base64
from typing import Dict, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RicohPasswordFlow:
    """
    Maneja el flujo de configuración de contraseñas de carpeta en impresoras Ricoh
    """
    
    def __init__(self, session: requests.Session, timeout: int = 30):
        """
        Initialize password flow handler
        
        Args:
            session: Authenticated requests session
            timeout: Request timeout in seconds
        """
        self.session = session
        self.timeout = timeout
    
    def set_folder_password(self, printer_ip: str, entry_index: str, password: str = "Temporal2021") -> bool:
        """
        Configura la contraseña de autenticación de carpeta siguiendo el flujo correcto de Ricoh
        
        Flujo:
        1. GET adrsGetUser.cgi (obtener formulario del usuario)
        2. POST adrEditPassword.cgi (abrir formulario de contraseña)
        3. POST adrEditPassword.cgi con contraseña en Base64
        4. POST adrsSetUser.cgi con isFolderAuthPasswordUpdated=true
        
        Args:
            printer_ip: IP de la impresora
            entry_index: Índice del usuario (ej: "00231")
            password: Contraseña a configurar (default: "Temporal2021")
            
        Returns:
            True si se configuró exitosamente, False en caso contrario
        """
        try:
            logger.info(f"🔐 Configurando contraseña de carpeta para usuario {entry_index} en {printer_ip}")
            logger.info(f"   Contraseña: {'***' if password else '(vacía)'}")
            
            # PASO 1: Obtener wimToken desde la lista
            list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
            logger.debug(f"   Paso 1: Obteniendo wimToken desde {list_url}")
            
            list_response = self.session.get(list_url, timeout=self.timeout)
            if list_response.status_code != 200:
                logger.error(f"❌ No se pudo acceder a la lista: {list_response.status_code}")
                return False
            
            # Extraer wimToken
            match = re.search(r'name="wimToken"\s+value="(\d+)"', list_response.text)
            if not match:
                logger.error("❌ No se encontró wimToken en la lista")
                return False
            
            wim_token = match.group(1)
            token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
            logger.debug(f"   ✅ wimToken obtenido: {token_preview}")
            
            # PASO 2: Obtener formulario del usuario
            get_user_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
            logger.debug(f"   Paso 2: Obteniendo formulario del usuario desde {get_user_url}")
            
            get_user_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',
                'kind': 'FOLDER',
                'inputSpecifyMode': 'FIX',
                'wayFrom': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
                'wayTo': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
                'pageSpecifiedIn': '',
                'pageNumberIn': '',
                'outputSpecifyModeIn': 'SETTINGS',
                'entryIndexIn': entry_index
            }
            
            user_form_response = self.session.post(
                get_user_url,
                data=get_user_data,
                timeout=self.timeout
            )
            
            if user_form_response.status_code != 200:
                logger.error(f"❌ No se pudo obtener formulario del usuario: {user_form_response.status_code}")
                return False
            
            # Extraer nuevo wimToken del formulario
            match = re.search(r'name="wimToken"\s+value="(\d+)"', user_form_response.text)
            if match:
                wim_token = match.group(1)
                token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
                logger.debug(f"   ✅ Nuevo wimToken del formulario: {token_preview}")
            
            # Extraer datos del usuario del formulario
            soup = BeautifulSoup(user_form_response.text, 'html.parser')
            
            user_name_input = soup.find('input', {'name': 'entryNameIn'})
            user_display_name_input = soup.find('input', {'name': 'entryDisplayNameIn'})
            user_code_input = soup.find('input', {'name': 'userCodeIn'})
            folder_path_input = soup.find('input', {'name': 'folderPathNameIn'})
            folder_username_input = soup.find('input', {'name': 'folderAuthUserNameIn'})
            
            user_name = user_name_input.get('value', '') if user_name_input else ''
            user_display_name = user_display_name_input.get('value', '') if user_display_name_input else ''
            user_code = user_code_input.get('value', '') if user_code_input else ''
            folder_path = folder_path_input.get('value', '') if folder_path_input else ''
            folder_username = folder_username_input.get('value', '') if folder_username_input else ''
            
            logger.debug(f"   Usuario: {user_name}, Código: {user_code}")
            logger.debug(f"   Carpeta: {folder_path}")
            logger.debug(f"   Usuario de red: {folder_username}")
            
            # Extraer funciones disponibles
            available_funcs = []
            func_checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})
            for checkbox in func_checkboxes:
                if checkbox.has_attr('checked') or checkbox.get('checked') in ['checked', 'true', '1']:
                    available_funcs.append(checkbox.get('value', ''))
            
            logger.debug(f"   Funciones: {available_funcs}")
            
            # PASO 3: Abrir formulario de edición de contraseña
            edit_password_url = f"http://{printer_ip}/web/entry/es/address/adrEditPassword.cgi"
            logger.debug(f"   Paso 3: Abriendo formulario de contraseña en {edit_password_url}")
            
            edit_password_open_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',
                'wayFrom': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
                'wayTo': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
                'pageSpecifiedIn': '',
                'pageNumberIn': '',
                'outputSpecifyModeIn': '',
                'kind': 'FOLDER',
                'inputSpecifyMode': 'NONE'
            }
            
            password_form_response = self.session.post(
                edit_password_url,
                data=edit_password_open_data,
                timeout=self.timeout
            )
            
            if password_form_response.status_code != 200:
                logger.error(f"❌ No se pudo abrir formulario de contraseña: {password_form_response.status_code}")
                return False
            
            # Extraer wimToken del formulario de contraseña
            match = re.search(r'name="wimToken"\s+value="(\d+)"', password_form_response.text)
            if match:
                wim_token = match.group(1)
                token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
                logger.debug(f"   ✅ wimToken del formulario de contraseña: {token_preview}")
            
            # PASO 4: Enviar contraseña codificada en Base64
            logger.debug(f"   Paso 4: Enviando contraseña codificada")
            
            # Codificar contraseña en Base64
            password_b64 = base64.b64encode(password.encode()).decode()
            logger.debug(f"   Contraseña en Base64: {password_b64}")
            
            edit_password_submit_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',
                'kind': 'FOLDER',
                'inputSpecifyMode': 'FIX',
                'wayFrom': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
                'wayTo': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
                'pageSpecifiedIn': '',
                'pageNumberIn': '',
                'outputSpecifyModeIn': '',
                'passwordIn': '',
                'wkpasswordIn': password_b64,
                'passwordConfirmIn': '',
                'wkpasswordConfirmIn': password_b64
            }
            
            password_submit_response = self.session.post(
                edit_password_url,
                data=edit_password_submit_data,
                timeout=self.timeout
            )
            
            if password_submit_response.status_code != 200:
                logger.error(f"❌ No se pudo enviar contraseña: {password_submit_response.status_code}")
                return False
            
            # Verificar si hay errores en la respuesta
            if 'Error' in password_submit_response.text or 'error' in password_submit_response.text:
                logger.error(f"❌ Error al configurar contraseña")
                # Guardar respuesta para debug
                with open('password_error_response.html', 'w', encoding='utf-8') as f:
                    f.write(password_submit_response.text)
                logger.debug(f"   Respuesta guardada en: password_error_response.html")
                return False
            
            logger.debug(f"   ✅ Contraseña enviada correctamente")
            
            # PASO 5: Volver a adrsGetUser.cgi para confirmar
            logger.debug(f"   Paso 5: Volviendo a formulario del usuario")
            
            # Extraer wimToken de la respuesta anterior
            match = re.search(r'name="wimToken"\s+value="(\d+)"', password_submit_response.text)
            if match:
                wim_token = match.group(1)
            
            get_user_confirm_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',
                'kind': 'FOLDER',
                'inputSpecifyMode': 'FIX',
                'wayFrom': 'adrsEditPassword.cgi?inputSpecifyMode=NONE&kind=FOLDER',
                'wayTo': 'adrsGetUser.cgi#AUTH_INFO_C?outputSpecifyModeIn=SETTINGS',
                'pageSpecifiedIn': '',
                'pageNumberIn': '',
                'outputSpecifyModeIn': 'SETTINGS'
            }
            
            confirm_response = self.session.post(
                get_user_url,
                data=get_user_confirm_data,
                timeout=self.timeout
            )
            
            if confirm_response.status_code != 200:
                logger.error(f"❌ No se pudo confirmar: {confirm_response.status_code}")
                return False
            
            # Extraer wimToken final
            match = re.search(r'name="wimToken"\s+value="(\d+)"', confirm_response.text)
            if match:
                wim_token = match.group(1)
                token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
                logger.debug(f"   ✅ wimToken final: {token_preview}")
            
            # PASO 6: Guardar usuario con isFolderAuthPasswordUpdated=true
            logger.debug(f"   Paso 6: Guardando usuario con contraseña actualizada")
            
            set_user_url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"
            
            # Construir payload completo
            set_user_data = [
                ('inputSpecifyModeIn', 'WRITE'),
                ('listUpdateIn', 'UPDATE'),
                ('wimToken', wim_token),
                ('mode', 'MODUSER'),
                ('pageSpecifiedIn', ''),
                ('pageNumberIn', ''),
                ('outputSpecifyModeIn', ''),
                ('inputSpecifyModeIn', ''),
                ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
                ('wayTo', 'adrsList.cgi'),
                ('isSelfPasswordEditMode', 'false'),
                ('isLocalAuthPasswordUpdated', 'false'),
                ('isFolderAuthPasswordUpdated', 'true'),  # ¡IMPORTANTE!
                ('entryIndexIn', entry_index),
                ('entryNameIn', user_name),
                ('entryDisplayNameIn', user_display_name),
                ('priorityIn', '5'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('entryTagInfoIn', '1'),
                ('userCodeIn', user_code),
                ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
                ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
                ('folderAuthUserNameIn', folder_username),
                ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
            ]
            
            # Agregar funciones disponibles
            for func in available_funcs:
                set_user_data.append(('availableFuncIn', func))
            
            # Continuar con campos restantes
            set_user_data.extend([
                ('entryUseIn', 'ENTRYUSE_TO_O'),
                ('entryUseIn', 'ENTRYUSE_FROM_O'),
                ('mailAddressIn', ''),
                ('isCertificateExist', 'false'),
                ('isEncryptAlways', 'false'),
                ('folderProtocolIn', 'SMB_O'),
                ('folderPathNameIn', folder_path),
            ])
            
            headers = {
                'Referer': f'http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            final_response = self.session.post(
                set_user_url,
                data=set_user_data,
                headers=headers,
                timeout=self.timeout
            )
            
            if final_response.status_code not in [200, 302]:
                logger.error(f"❌ No se pudo guardar usuario: {final_response.status_code}")
                return False
            
            # Verificar errores en la respuesta
            if 'BADFLOW' in final_response.text:
                logger.error(f"❌ BADFLOW detectado al guardar")
                return False
            
            if 'BUSY' in final_response.text or 'está siendo utilizado' in final_response.text:
                logger.error(f"❌ Impresora ocupada")
                return "BUSY"
            
            if 'Error' in final_response.text or 'error' in final_response.text:
                logger.warning(f"⚠️  Posible error en respuesta final")
                # Guardar para debug
                with open('final_save_response.html', 'w', encoding='utf-8') as f:
                    f.write(final_response.text)
                logger.debug(f"   Respuesta guardada en: final_save_response.html")
            
            logger.info(f"✅ Contraseña de carpeta configurada exitosamente para usuario {entry_index}")
            return True
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout al configurar contraseña")
            return "TIMEOUT"
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Error de conexión al configurar contraseña")
            return "CONNECTION"
        except Exception as e:
            logger.error(f"❌ Error configurando contraseña: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
