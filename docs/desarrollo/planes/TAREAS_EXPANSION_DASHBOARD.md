# Tareas: Expansión del Dashboard y Validación SNMP/HTTP de Flota

Este checklist detalla los pasos secuenciales para ejecutar la expansión del dashboard principal y las validaciones de consumibles una vez concluida la fase de verificación previa.

---

## 🛠️ Fase 1: Corrección de Estabilidad y Conectividad (Backend)
- [ ] Modificar `backend/api/dashboard.py` para importar `Printer` desde `db.models` y resolver el error `NameError: Printer`.
- [ ] Probar el endpoint `/api/v1/dashboard/toner-alertas` localmente para garantizar una respuesta 200 OK limpia.
- [ ] Diseñar la validación activa de puerto `161` para comprobar el estado de SNMP de la impresora.
- [ ] Desarrollar la lógica de fallback de Web Scraping HTTP para Ricoh Web Image Monitor:
  - [ ] Consumir `/web/guest/es/websys/status/getDeviceStatus.cgi` (XML de estado).
  - [ ] Parsear la página HTML `/web/guest/es/websys/status/configuration.cgi` usando `BeautifulSoup` para extraer el porcentaje de tóner si SNMP falla.

---

## 🎨 Fase 2: Componentes del Frontend (React & TypeScript)
- [ ] **Modificar Hooks de Datos:**
  - [ ] Agregar la interfaz `EvolutionItem` en `src/hooks/useDashboardData.ts`.
  - [ ] Implementar el hook `useEvolutionData` consumiendo el endpoint `/api/v1/analytics/evolution?meses=6`.
- [ ] **Expandir `OverviewDashboard.tsx`:**
  - [ ] Integrar y desestructurar `useEvolutionData`.
  - [ ] **Widget Analítico:** Añadir una sección de gráfico de área suave (`AreaChart` con degradados HSL fluidos) para la evolución de volumen de páginas de los últimos 6 meses.
  - [ ] **Widget Sostenible (Ricoh Green):** Implementar la tarjeta ecológicamente premium con efecto de vidrio (glassmorphism), bordes redondeados y micro-animaciones:
    - [ ] Cálculo de Árboles Preservados.
    - [ ] Cálculo de CO2 Evitado en kg.
    - [ ] Cálculo de Agua Conservada en Litros.
  - [ ] **Widget Operations Desk / Diagnósticos:** Crear el panel interactivo superior con:
    - [ ] Mensajes de diagnóstico de conectividad (Equipos offline).
    - [ ] Alertas de tóner crítico (<15%).
    - [ ] Indicador de protocolo activo (SNMP vs. HTTP Web Image Monitor).
    - [ ] Botones con iconos de Lucide para resolver problemas e ir directamente a aprovisionar o leer contadores.

---

## 🚀 Fase 3: Pruebas, Compilación y Cierre
- [ ] Validar la correcta adaptación responsive (móviles, tabletas, laptops) de los nuevos widgets en `OverviewDashboard.tsx`.
- [ ] Ejecutar el comando de producción para garantizar una compilación limpia sin errores de tipos de TypeScript:
  ```powershell
  npm run build
  ```
- [ ] Realizar pruebas cruzadas simulando la desactivación del puerto 161 (SNMP) y comprobar que el fallback HTTP responda correctamente.
- [ ] Crear el reporte walkthrough definitivo y el consolidado del hito.
