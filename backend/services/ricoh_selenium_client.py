import os
import time
import re
import logging
import requests
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

# Mapa global de funciones para consistencia
FUNC_MAP = {
    'COPY': 'copiadora',
    'SCAN': 'escaner',
    'PRT': 'impresora',
    'PRINT': 'impresora',
    'DBX': 'document_server',
    'DOC_SERVER': 'document_server',
    'FAX': 'fax',
    'MFPBROWSER': 'navegador',
    'BROWSER': 'navegador'
}

class RicohSeleniumClient:
    def __init__(self):
        self.driver = None

    def _init_driver(self):
        if self.driver is None:
            logger.info("   🌐 Iniciando Driver Selenium...")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Silenciar logs de devtools
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _ensure_session_cookies(self, printer_ip: str):
        """Intenta asegurar que el dominio es correcto antes de añadir cookies"""
        try:
            if not self.driver.current_url.startswith(f"http://{printer_ip}"):
                self.driver.get(f"http://{printer_ip}/")
                time.sleep(1)
            
            # Verificar si aterrizamos en error de cookies
            if "Error" in self.driver.title or "Cookie" in self.driver.title:
                logger.info("   🍪 Saltando error de cookies...")
                self.driver.get(f"http://{printer_ip}/web/guest/es/websys/webArch/mainFrame.cgi")
                time.sleep(1)
                self.driver.get(f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi")
                time.sleep(1)
        except Exception as e:
            logger.warning(f"   ⚠️ Error al asegurar cookies: {e}")

    def _prepare_navigation_state(self, printer_ip: str):
        """Prepara el estado de navegación visitando la lista primero para evitar BADFLOW"""
        try:
             self._ensure_session_cookies(printer_ip)
             logger.info("   📋 Asegurando contexto en adrsList...")
             self.driver.get(f"http://{printer_ip}/web/entry/es/address/adrsList.cgi")
             time.sleep(2)
        except Exception as e:
             logger.warning(f"   ⚠️ Error al preparar navegación: {e}")

    def sync_cookies_from_requests(self, session: requests.Session, printer_ip: str):
        """Copia las cookies de una sesión de requests al driver de Selenium."""
        try:
            logger.info("   🍪 Sincronizando cookies de HTTP a Selenium...")
            if not self.driver.current_url.startswith(f"http://{printer_ip}"):
                self.driver.get(f"http://{printer_ip}/")
            
            for cookie in session.cookies:
                cookie_dict = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'path': cookie.path if cookie.path else '/'
                }
                try:
                    self.driver.add_cookie(cookie_dict)
                    logger.debug(f"      Cookie añadida: {cookie.name}={cookie.value[:10]}...")
                except Exception as ce:
                    logger.debug(f"      No se pudo añadir cookie {cookie.name}: {ce}")
            
            driver_cookies = self.driver.get_cookies()
            logger.info(f"   📊 Cookies en el driver: {[c['name'] for c in driver_cookies]}")
            logger.info("   ✅ Cookies sincronizadas correctamente")
        except Exception as e:
            logger.warning(f"   ⚠️ Error sincronizando cookies: {e}")

    def _navigate_to_user_edit(self, printer_ip: str, entry_index: str, admin_user: str, admin_password: str, http_session: requests.Session = None) -> bool:
        """Navega a la página de edición de un usuario, manejando login y cookies."""
        try:
            self._init_driver()
            wait = WebDriverWait(self.driver, 15)

            if http_session:
                self.sync_cookies_from_requests(http_session, printer_ip)

            self._prepare_navigation_state(printer_ip)
            
            wim_token = ""
            try:
                match = re.search(r'name="wimToken"\s+value="(\d+)"', self.driver.page_source)
                if match: wim_token = match.group(1)
            except: pass

            edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi?mode=EDIT&entryIndexIn={entry_index}"
            if wim_token:
                edit_url += f"&wimToken={wim_token}"
            
            logger.info(f"   SELENIUM: Navegando a edición: {edit_url}")
            self.driver.get(edit_url)
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            needs_login = "authForm" in current_url or "400" in page_source or \
                          len(self.driver.find_elements(By.NAME, "userid_work")) > 0
            
            if needs_login:
                logger.info("   🔐 Sesión requerida en Selenium. Iniciando login...")
                self.driver.get(f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi")
                time.sleep(1)
                
                try:
                    user_f = wait.until(EC.presence_of_element_located((By.NAME, "userid_work")))
                    user_f.clear()
                    user_f.send_keys(admin_user)
                    try:
                        pass_f = self.driver.find_element(By.NAME, "password_work")
                        pass_f.clear()
                        if admin_password: pass_f.send_keys(admin_password)
                    except: pass
                    
                    self.driver.execute_script("if(typeof encrypt==='function')encrypt(); document.forms['form1'].submit();")
                    time.sleep(3)
                    
                    self._prepare_navigation_state(printer_ip)
                    self.driver.get(edit_url)
                except Exception as e:
                    logger.error(f"   ❌ Error en login Selenium: {e}")
                    return False
            
            try:
                wait.until(EC.presence_of_element_located((By.NAME, "entryNameIn")))
                return True
            except:
                logger.error("   ❌ No se encontró entryNameIn tras navegación/login")
                # Depurar qué hay en pantalla
                fail_file = f"selenium_fail_{entry_index}.html"
                with open(fail_file, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                logger.error(f"   📄 HTML guardado en {fail_file}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Error navegando a edición: {e}")
            return False

    def get_user_permissions(self, printer_ip: str, entry_index: str, admin_user: str = "admin", admin_password: str = "", http_session: requests.Session = None) -> Optional[Dict]:
        logger.info(f"🚀 SELENIUM: Reading permissions for index={entry_index} on {printer_ip}")
        try:
            if not self._navigate_to_user_edit(printer_ip, entry_index, admin_user, admin_password, http_session):
                return None

            permisos = {
                'copiadora': False, 'copiadora_color': False,
                'impresora': False, 'impresora_color': False,
                'escaner': False, 'document_server': False,
                'fax': False, 'navegador': False
            }
            
            checkboxes = self.driver.find_elements(By.NAME, "availableFuncIn")
            if not checkboxes:
                checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")

            found_any = False
            for cb in checkboxes:
                try:
                    val = cb.get_attribute("value").upper()
                    if not cb.is_selected(): continue
                    
                    for k, pk in FUNC_MAP.items():
                        if k in val:
                            if pk == 'copiadora':
                                if any(x in val for x in ['COLOR', 'FULL']): permisos['copiadora_color'] = True
                                else: permisos['copiadora'] = True
                            elif pk == 'impresora':
                                if any(x in val for x in ['COLOR', 'FULL']): permisos['impresora_color'] = True
                                else: permisos['impresora'] = True
                            else:
                                permisos[pk] = True
                            found_any = True
                            break
                except: pass
            
            logger.info(f"   ✅ Permisos leídos: {permisos}")
            return permisos if found_any else None
            
        except Exception as e:
            logger.error(f"❌ Error en get_user_permissions: {e}")
            return None

    def set_user_permissions(self, printer_ip: str, entry_index: str, permissions: Dict, admin_user: str = "admin", admin_password: str = "", http_session: requests.Session = None) -> bool:
        logger.info(f"🚀 SELENIUM: Setting permissions for index={entry_index} on {printer_ip}")
        try:
            if not self._navigate_to_user_edit(printer_ip, entry_index, admin_user, admin_password, http_session):
                return False

            logger.info("3. Ajustando checkboxes...")
            checkboxes = self.driver.find_elements(By.NAME, "availableFuncIn")
            if not checkboxes:
                checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")

            changes = 0
            for cb in checkboxes:
                try:
                    val = cb.get_attribute("value").upper()
                    p_key = None
                    for k, pk in FUNC_MAP.items():
                        if k in val:
                            if pk == 'copiadora':
                                if any(x in val for x in ['COLOR', 'FULL']): p_key = 'copiadora_color'
                                else: p_key = 'copiadora'
                            elif pk == 'impresora':
                                if any(x in val for x in ['COLOR', 'FULL']): p_key = 'impresora_color'
                                else: p_key = 'impresora'
                            else:
                                p_key = pk
                            break
                    
                    if p_key and p_key in permissions:
                        should_be = permissions[p_key]
                        is_now = cb.is_selected()
                        if should_be != is_now:
                            logger.info(f"   Ajustando {p_key} ({val}): {is_now} -> {should_be}")
                            self.driver.execute_script("arguments[0].checked = arguments[1];", cb, should_be)
                            changes += 1
                except: pass

            logger.info(f"4. Enviando formulario ({changes} cambios)...")
            try:
                # Buscar botón Aceptar
                btn = self.driver.find_element(By.XPATH, "//*[@id='Aceptar' or contains(text(), 'Aceptar')]")
                btn.click()
            except:
                # Fallback: disparar el envío del formulario si existe
                self.driver.execute_script("if(document.forms['form1']) document.forms['form1'].submit();")
            
            time.sleep(3)
            logger.info("✅ Operación completada en Selenium")
            return True
        except Exception as e:
            logger.error(f"❌ Error en set_user_permissions: {e}")
            return False

# Singleton
_selenium_client = None

def get_selenium_client():
    global _selenium_client
    if _selenium_client is None:
        _selenium_client = RicohSeleniumClient()
    return _selenium_client


def close_selenium_client():
    """Cierra el cliente Selenium si está activo"""
    global _selenium_client
    if _selenium_client is not None:
        try:
            _selenium_client.close()
        except Exception as e:
            logger.warning(f"Error cerrando Selenium client: {e}")
        finally:
            _selenium_client = None
