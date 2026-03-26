"""
Ricoh Authentication Service
Maneja autenticación unificada para impresoras Ricoh
"""
import requests
import re
import base64
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADMIN_USER = "admin"
ADMIN_PASS = ""


class RicohAuthService:
    """Servicio de autenticación para impresoras Ricoh"""
    
    @staticmethod
    def login_to_printer(session: requests.Session, printer_ip: str) -> None:
        """
        Login a la impresora - detecta automáticamente el método correcto
        
        Soporta:
        - Método especial para impresoras 252 y 253
        - Método estándar para otras impresoras
        
        Args:
            session: Sesión de requests
            printer_ip: IP de la impresora
            
        Raises:
            Exception: Si el login falla
        """
        # Detectar si es la impresora 252 o 253 (requieren método especial)
        if printer_ip in ["192.168.91.252", "192.168.91.253"]:
            RicohAuthService._login_special_method(session, printer_ip)
        else:
            RicohAuthService._login_standard_method(session, printer_ip)
    
    @staticmethod
    def _login_special_method(session: requests.Session, printer_ip: str) -> None:
        """Método de login especial para impresoras 252 y 253"""
        auth_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi?open=websys/status/getUnificationCounter.cgi"
        auth_resp = session.get(auth_url, timeout=10)
        
        soup = BeautifulSoup(auth_resp.text, 'html.parser')
        wim_token_input = soup.find('input', {'name': 'wimToken'})
        wim_token = wim_token_input.get('value') if wim_token_input else None
        
        login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
        
        login_data = {
            'userid': base64.b64encode(ADMIN_USER.encode()).decode(),
            'password': base64.b64encode(ADMIN_PASS.encode()).decode(),
            'userid_work': '',
            'password_work': ''
        }
        
        if wim_token:
            login_data['wimToken'] = wim_token
        
        session.post(login_url, data=login_data, timeout=10)
    
    @staticmethod
    def _login_standard_method(session: requests.Session, printer_ip: str) -> None:
        """Método de login estándar para la mayoría de impresoras"""
        login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
        form_resp = session.get(login_form_url, timeout=10)
        token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
        login_token = token_match.group(1) if token_match else ""
        
        userid_b64 = base64.b64encode(ADMIN_USER.encode()).decode()
        login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
        login_data = {
            'wimToken': login_token,
            'userid_work': '',
            'userid': userid_b64,
            'password_work': '',
            'password': ADMIN_PASS,
            'open': '',
        }
        
        session.post(login_url, data=login_data, timeout=10, allow_redirects=True)
