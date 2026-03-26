#!/usr/bin/env python3
"""
Script de Pruebas de Integración
Prueba el sistema completo end-to-end
"""
import requests
import sys
import time
from typing import Dict, Any

# Colores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Configuración
API_BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "superadmin",
    "password": "{:Z75M!=x>9PiPp2"
}

class IntegrationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.test_empresa_id = None
        self.test_printer_id = None
        
    def print_test(self, name: str):
        p