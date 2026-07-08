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
        if isinstance(timeout, (int, float)):
            self.timeout = (3.05, float(timeout))
        else:
            self.timeout = timeout
    
    def set_folder_password(self, printer_ip: str, entry_index: str, password: str = "Temporal2021", wim_token: Optional[str] = None) -> bool:
        """
        Configura la contraseña de autenticación de carpeta siguiendo el flujo correcto de Ricoh
        
        Flujo:
        1. GET adrsList.cgi (obtener formulario del usuario) [Se salta si se proporciona wim_token]
        2. POST adrsGetUser.cgi (MODUSER)
        3. POST adrEditPassword.cgi (abrir formulario de contraseña)
        4. POST adrEditPassword.cgi con contraseña en Base64
        5. POST adrsSetUser.cgi con isFolderAuthPasswordUpdated=true
        
        Args:
            printer_ip: IP de la impresora
            entry_index: Índice del usuario (ej: "00231")
            password: Contraseña a configurar (default: "Temporal2021")
            wim_token: Token WIM activo para saltar el primer GET a la lista
            
        Returns:
            True si se configuró exitosamente, False en caso contrario
        """
        try:
            logger.info(f"🔐 Configurando contraseña de carpeta para usuario {entry_index} en {printer_ip}")
            logger.info(f"   Contraseña: {'***' if password else '(vacía)'}")
            
            if not wim_token:
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
                logger.debug(f"   ✅ wimToken obtenido de la lista: {token_preview}")
            else:
                token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
                logger.debug(f"   ✅ Usando wimToken proporcionado: {token_preview}")
            
            # FIX 1: Normalizar entry_index a 5 dígitos con ceros a la izquierda.
            # find_specific_user puede devolver '231' pero adrsGetUser.cgi requiere '00231'.
            # Si ya tiene 5+ dígitos, dejarlo como está.
            try:
                entry_index = str(int(entry_index)).zfill(5)
            except (ValueError, TypeError):
                pass  # Si no es numérico, dejarlo como está
            logger.info(f"   📋 entry_index normalizado: {entry_index}")

            # 1.5 Cargar el batch que contiene este usuario (CRÍTICO para evitar BADFLOW/TIMEOUT en el WIM)
            try:
                entry_idx_numeric = int(entry_index)
                batch = (entry_idx_numeric // 50) + 1
                
                ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
                ajax_data = {
                    'wimToken': wim_token,
                    'listCountIn': '50',
                    'getCountIn': str(batch)
                }
                ajax_headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsList.cgi",
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                logger.debug(f"   📋 Cargando lote AJAX {batch} para entry_index {entry_index}...")
                self.session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=self.timeout)
            except Exception as e_ajax:
                logger.warning(f"   ⚠️  Fallo al cargar batch AJAX en flujo de contraseña: {e_ajax}")

            # PASO 2: Obtener formulario del usuario (MODUSER desde la lista)
            get_user_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
            logger.debug(f"   Paso 2: Obteniendo formulario del usuario desde {get_user_url}")
            
            get_user_data = {
                'wimToken': wim_token,
                'mode': 'MODUSER',
                'outputSpecifyModeIn': 'PROGRAMMED',
                'entryIndexIn': entry_index
            }
            
            user_form_response = self.session.post(
                get_user_url,
                data=get_user_data,
                headers={
                    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsList.cgi",
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=self.timeout
            )
            
            if user_form_response.status_code != 200:
                logger.error(f"❌ No se pudo obtener formulario del usuario: {user_form_response.status_code}")
                return False
            
            # FIX 2: Detectar TIMEOUT real vs falso positivo.
            # La página adrsList NORMAL contiene 'Tiempo de sesión agotado' en su JS de recuperación.
            # Solo es un TIMEOUT real si la página tiene class="errorMessage" Y el returnValue=TIMEOUT.
            is_real_timeout = (
                'returnValue" value="TIMEOUT' in user_form_response.text and
                'class="errorMessage"' in user_form_response.text
            )
            if is_real_timeout:
                logger.error("❌ TIMEOUT real al obtener formulario MODUSER (paso 2) — WIM session expirada")
                with open('password_step2_error.html', 'w', encoding='utf-8') as f:
                    f.write(user_form_response.text)
                return "TIMEOUT"
            
            # FIX 3: Detectar cuando MODUSER falla silenciosamente devolviendo la lista en vez del form de edición.
            # Si el usuario no existe en entry_index dado, el printer devuelve la lista sin error visible.
            if 'entryNameIn' not in user_form_response.text and 'userCodeIn' not in user_form_response.text:
                logger.error(f"❌ MODUSER devolvió la página de lista (no el formulario de edición).")
                logger.error(f"   → entry_index '{entry_index}' probablemente no existe en la impresora.")
                with open('password_step2_error.html', 'w', encoding='utf-8') as f:
                    f.write(user_form_response.text)
                return False
            
            # Extraer nuevo wimToken del formulario
            match = re.search(r'name="wimToken"\s+value="(\d+)"', user_form_response.text)
            if not match:
                logger.error("❌ No se encontró wimToken en la respuesta del formulario del usuario (paso 2)")
                with open('password_step2_error.html', 'w', encoding='utf-8') as f:
                    f.write(user_form_response.text)
                return False
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
            edit_password_url = f"http://{printer_ip}/web/entry/es/address/adrsEditPassword.cgi"
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
                headers={
                    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi",
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=self.timeout
            )
            
            if password_form_response.status_code != 200:
                logger.error(f"❌ No se pudo abrir formulario de contraseña: {password_form_response.status_code}")
                return False
            
            # Detectar fallo temprano: TIMEOUT en el paso 3
            if 'Tiempo de sesión agotado' in password_form_response.text or 'returnValue" value="TIMEOUT' in password_form_response.text:
                logger.error("❌ TIMEOUT al abrir formulario de contraseña (paso 3) — el printer rechazó el flujo MODUSER")
                with open('password_step3_error.html', 'w', encoding='utf-8') as f:
                    f.write(password_form_response.text)
                return "TIMEOUT"
            
            # Extraer wimToken del formulario de contraseña
            match = re.search(r'name="wimToken"\s+value="(\d+)"', password_form_response.text)
            if not match:
                logger.error("❌ No se encontró wimToken en el formulario de contraseña (paso 3)")
                with open('password_step3_error.html', 'w', encoding='utf-8') as f:
                    f.write(password_form_response.text)
                return False
            wim_token = match.group(1)
            token_preview = f"{wim_token[:4]}...{wim_token[-4:]}" if len(wim_token) > 8 else wim_token
            logger.info(f"   ✅ wimToken del formulario de contraseña: {token_preview}")
            
            # PASO 4: Enviar contraseña codificada en Base64
            logger.info(f"   Paso 4: Enviando contraseña codificada")
            
            # Codificar contraseña en Base64
            password_b64 = base64.b64encode(password.encode()).decode()
            logger.info(f"   Contraseña en Base64 (codificada)")
            
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
                # Enviar en ambas variantes de campos para compatibilidad universal
                'passwordIn': password_b64,
                'passwordInwk': password_b64,
                'wkpasswordIn': password_b64,
                'passwordConfirmIn': password_b64,
                'passwordConfirmInwk': password_b64,
                'wkpasswordConfirmIn': password_b64
            }
            
            password_submit_response = self.session.post(
                edit_password_url,
                data=edit_password_submit_data,
                headers={
                    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsEditPassword.cgi",
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=self.timeout
            )
            
            if password_submit_response.status_code != 200:
                logger.error(f"❌ No se pudo enviar contraseña: {password_submit_response.status_code}")
                return False
            
            # Verificar si hay errores reales de Ricoh en la respuesta (evitar falsos positivos)
            if 'Tiempo de sesión agotado' in password_submit_response.text or 'returnValue" value="TIMEOUT' in password_submit_response.text:
                logger.error(f"❌ TIMEOUT al enviar contraseña (paso 4)")
                with open('password_error_response.html', 'w', encoding='utf-8') as f:
                    f.write(password_submit_response.text)
                return "TIMEOUT"
            
            if 'class="errorMessage"' in password_submit_response.text and 'messageIconE' in password_submit_response.text:
                logger.error(f"❌ Error al configurar contraseña (paso 4) — página de error del printer")
                with open('password_error_response.html', 'w', encoding='utf-8') as f:
                    f.write(password_submit_response.text)
                return False
            
            logger.info(f"   ✅ Contraseña enviada correctamente")
            
            # PASO 5: Volver a adrsGetUser.cgi para confirmar
            logger.info(f"   Paso 5: Volviendo a formulario del usuario")
            
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
                headers={
                    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsEditPassword.cgi",
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
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
                logger.info(f"   ✅ wimToken final: {token_preview}")
            
            # PASO 6: Guardar usuario con isFolderAuthPasswordUpdated=true
            logger.info(f"   Paso 6: Guardando usuario con contraseña actualizada")
            
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
                ('isFolderAuthPasswordUpdated', 'false'),  # false para consolidar la contraseña temporal ingresada en la subpágina
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
