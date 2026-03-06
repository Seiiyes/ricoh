# Requirements Document

## Introduction

Este documento define los requisitos para el módulo frontend de contadores del sistema de gestión de impresoras Ricoh. El módulo permitirá a los usuarios visualizar, consultar y gestionar contadores de impresión a través de una interfaz web moderna construida con React y TypeScript.

El backend REST API ya está implementado (Fase 4) con 9 endpoints que proporcionan acceso completo a contadores totales, contadores por usuario, lecturas manuales, cierres mensuales e históricos.

### CRITICAL REQUIREMENT CLARIFICATION

**Daily Closes (Not Monthly):**
- The system requires DAILY close functionality, not monthly closes
- Users select a specific date (e.g., March 2, 2026)
- System compares counters with the same day of the previous month (e.g., February 2, 2026)
- Differences are calculated between these two specific dates

**User Counters Display:**
- User counter table MUST be visible in Printer Detail View
- Data is fetched from existing endpoint: /api/counters/users/{printer_id}
- Shows cumulative totals per user (not differences)

**Backend Limitation:**
- Current backend only supports monthly closes (entire month comparison)
- Backend needs new endpoint for daily closes with specific date comparison
- See Requirement 8 for backend API extension details

### Existing Project Context

El proyecto ya tiene una estructura frontend establecida con:
- **Stack**: React 19 + TypeScript + Vite
- **UI**: Tailwind CSS con tema personalizado (ricoh-red: #E60012, industrial-gray: #1E293B)
- **Icons**: Lucide React (ya instalado)
- **State**: Zustand para estado global (usado en módulo de usuarios)
- **Navigation**: Menú lateral con vistas (Descubrir, Crear Usuarios, Administrar Usuarios)
- **Patterns**: Cards con sombras, tablas con paginación (50 items), modales para edición
- **Services**: Patrón establecido con `API_BASE_URL` desde env variables

## Glossary

- **Counter_Module**: Módulo frontend de React que gestiona la visualización y operaciones de contadores
- **Counter_Service**: Servicio TypeScript que encapsula las llamadas HTTP a la API de contadores
- **Dashboard_View**: Vista principal que muestra resumen de contadores de todas las impresoras
- **Printer_Detail_View**: Vista detallada de contadores de una impresora específica
- **Daily_Close_View**: Vista para realizar y consultar cierres diarios
- **User_Counter_Table**: Componente tabla que muestra contadores acumulados por usuario
- **History_Chart**: Componente gráfico que visualiza tendencias de contadores
- **Export_Service**: Servicio que genera reportes en Excel/PDF
- **Loading_Indicator**: Componente visual que indica operaciones en progreso
- **Error_Handler**: Componente que muestra mensajes de error al usuario

## Requirements

### Requirement 1: Counter Service API Integration

**User Story:** Como desarrollador, quiero un servicio TypeScript que encapsule todas las llamadas a la API de contadores, para que el código de componentes sea limpio y reutilizable.

#### Acceptance Criteria

1. THE Counter_Service SHALL provide a function to fetch the latest total counter for a printer
2. THE Counter_Service SHALL provide a function to fetch counter history with optional date filters
3. THE Counter_Service SHALL provide a function to fetch user counters for a printer
4. THE Counter_Service SHALL provide a function to fetch user counter history with filters
5. THE Counter_Service SHALL provide a function to trigger manual counter reading
6. THE Counter_Service SHALL provide a function to trigger reading all printers
7. THE Counter_Service SHALL provide a function to perform daily close with specific date
8. THE Counter_Service SHALL provide a function to fetch daily closes with optional date range filter
9. THE Counter_Service SHALL provide a function to fetch a specific daily close
10. WHEN an API call fails, THE Counter_Service SHALL throw an error with descriptive message
11. THE Counter_Service SHALL use the API_BASE_URL from environment variables
12. FOR ALL API functions, calling with valid parameters then parsing the response SHALL produce valid TypeScript types (round-trip property)

### Requirement 2: Dashboard View

**User Story:** Como usuario, quiero ver un dashboard con el resumen de contadores de todas las impresoras, para tener una vista general del estado del sistema.

#### Acceptance Criteria

1. THE Dashboard_View SHALL display a card for each registered printer using existing card styling patterns
2. WHEN the Dashboard_View loads, THE Dashboard_View SHALL fetch the list of printers using printerService
3. FOR EACH printer card, THE Dashboard_View SHALL display hostname, IP address, and location
4. FOR EACH printer card, THE Dashboard_View SHALL display the last total counter value
5. FOR EACH printer card, THE Dashboard_View SHALL display the last reading timestamp
6. WHEN a printer card is clicked, THE Dashboard_View SHALL navigate to Printer_Detail_View
7. THE Dashboard_View SHALL display a "Read All Printers" button styled with ricoh-red background
8. WHEN "Read All Printers" is clicked, THE Dashboard_View SHALL trigger counter reading for all printers
9. WHILE reading all printers, THE Dashboard_View SHALL display Loading_Indicator using Loader2 from lucide-react
10. WHEN reading completes, THE Dashboard_View SHALL display success count and failure count
11. IF reading fails for any printer, THE Dashboard_View SHALL display error details
12. THE Dashboard_View SHALL be responsive for desktop and tablet viewports (min-width: 768px)
13. THE Dashboard_View SHALL use Tailwind classes consistent with existing components (bg-white, rounded-lg, shadow-sm, border-slate-200)

### Requirement 3: Printer Detail View

**User Story:** Como usuario, quiero ver el detalle completo de contadores de una impresora, para analizar su uso específico.

#### Acceptance Criteria

1. THE Printer_Detail_View SHALL display printer identification (hostname, IP, serial number) in a card with bg-white, rounded-lg, shadow-sm
2. THE Printer_Detail_View SHALL display the complete counter breakdown (B/N, Color by function) using existing card patterns
3. THE Printer_Detail_View SHALL display counters for: copiadora, impresora, fax, escaner in separate sections
4. THE Printer_Detail_View SHALL display the last reading timestamp formatted as locale string
5. THE Printer_Detail_View SHALL display a "Manual Read" button styled with bg-ricoh-red text-white rounded-full
6. WHEN "Manual Read" is clicked, THE Printer_Detail_View SHALL trigger counter reading for that printer
7. WHILE reading counters, THE Printer_Detail_View SHALL display Loading_Indicator using Loader2 with animate-spin
8. WHEN reading completes, THE Printer_Detail_View SHALL refresh displayed counters
9. IF reading fails, THE Printer_Detail_View SHALL display error message via Error_Handler
10. THE Printer_Detail_View SHALL display History_Chart with counter trends
11. THE Printer_Detail_View SHALL display User_Counter_Table with user consumption data from /api/counters/users/{printer_id}
12. THE Printer_Detail_View SHALL provide navigation back to Dashboard_View using existing navigation patterns

### Requirement 4: Counter History Visualization

**User Story:** Como usuario, quiero ver gráficos de tendencias de contadores, para identificar patrones de uso a lo largo del tiempo.

#### Acceptance Criteria

1. THE History_Chart SHALL display total counter evolution over time using a charting library (recharts recommended)
2. THE History_Chart SHALL display separate lines for: total, copiadora, impresora, escaner with distinct colors
3. THE History_Chart SHALL support date range filtering (last 7 days, 30 days, 90 days, all) using button group with existing styles
4. WHEN a date range is selected, THE History_Chart SHALL fetch filtered history data
5. THE History_Chart SHALL display timestamps on X-axis and counter values on Y-axis
6. THE History_Chart SHALL display tooltips on hover showing exact values
7. THE History_Chart SHALL handle empty data gracefully with "No data available" message in text-slate-400
8. THE History_Chart SHALL use responsive sizing to fit container width
9. FOR ALL counter values displayed, the sum of function counters SHALL be less than or equal to total counter (invariant property)
10. THE History_Chart SHALL be wrapped in a card with bg-white, rounded-lg, shadow-sm, border-slate-200

### Requirement 5: User Counter Table

**User Story:** Como usuario, quiero ver una tabla de contadores acumulados por usuario en la vista de detalle de impresora, para identificar quién usa más la impresora.

#### Acceptance Criteria

1. THE User_Counter_Table SHALL display columns: código, nombre, total páginas, B/N, color
2. THE User_Counter_Table SHALL display breakdown by function (copiadora, impresora, escaner, fax)
3. THE User_Counter_Table SHALL fetch data from /api/counters/users/{printer_id} endpoint
4. THE User_Counter_Table SHALL display cumulative totals per user (not differences)
5. THE User_Counter_Table SHALL support sorting by any column (ascending/descending)
6. WHEN a column header is clicked, THE User_Counter_Table SHALL sort by that column
7. THE User_Counter_Table SHALL support filtering by user name or code
8. WHEN filter text is entered, THE User_Counter_Table SHALL show only matching users
9. THE User_Counter_Table SHALL display pagination controls for more than 50 users (matching project standard)
10. THE User_Counter_Table SHALL display total count of users
11. THE User_Counter_Table SHALL handle empty data with "No users found" message
12. FOR EACH user row, total_paginas SHALL equal total_bn plus total_color (invariant property)
13. THE User_Counter_Table SHALL use existing table styling patterns (bg-white, rounded-lg, shadow-sm)
14. THE User_Counter_Table SHALL be visible in Printer_Detail_View below the counter breakdown

### Requirement 6: Daily Close Operations

**User Story:** Como administrador, quiero realizar cierres diarios de contadores seleccionando una fecha específica, para comparar contadores con el mismo día del mes anterior y generar reportes contables.

#### Acceptance Criteria

1. THE Daily_Close_View SHALL display a form with fields: printer, date, closed_by, notes in a card with bg-white, rounded-lg, shadow-sm
2. THE Daily_Close_View SHALL populate printer dropdown with all registered printers using border-slate-200 styling
3. THE Daily_Close_View SHALL provide a date picker for selecting the close date (e.g., March 2, 2026)
4. WHEN form is submitted, THE Daily_Close_View SHALL validate all required fields
5. IF selected date is in the future, THE Daily_Close_View SHALL display validation error in text-error
6. WHEN validation passes, THE Daily_Close_View SHALL call Counter_Service to perform daily close
7. THE Daily_Close_View SHALL calculate differences by comparing selected date with same day of previous month (e.g., March 2 vs February 2)
8. WHEN close succeeds, THE Daily_Close_View SHALL display success message with differences in text-success
9. IF close fails due to duplicate, THE Daily_Close_View SHALL display "Close already exists for this date" error
10. IF close fails due to no counters, THE Daily_Close_View SHALL display "No counters available for selected date" error
11. IF counters for comparison date (previous month same day) do not exist, THE Daily_Close_View SHALL display warning message
12. THE Daily_Close_View SHALL display table of previous closes for selected printer using existing table patterns
13. THE Daily_Close_View SHALL display differences vs comparison date for each close with color coding (green for positive, red for negative)
14. THE Daily_Close_View form submit button SHALL be styled with bg-industrial-gray text-white rounded-full

### Requirement 7: Daily Close History

**User Story:** Como usuario, quiero consultar cierres diarios anteriores, para revisar históricos contables y comparaciones entre fechas.

#### Acceptance Criteria

1. THE Daily_Close_View SHALL display a table of daily closes with bg-white, rounded-lg, shadow-sm, border-slate-200
2. THE Daily_Close_View SHALL display columns: date, total pages, differences, closed by, timestamp
3. THE Daily_Close_View SHALL support filtering by date range using date pickers with existing styles
4. WHEN a date range filter is selected, THE Daily_Close_View SHALL fetch closes for that range only
5. THE Daily_Close_View SHALL display closes in descending chronological order (newest first)
6. THE Daily_Close_View SHALL display difference values with color coding (text-success for positive, text-error for negative)
7. THE Daily_Close_View SHALL display comparison date for each close (e.g., "vs Feb 2, 2026")
8. THE Daily_Close_View SHALL display "Export" button for each close styled with text-xs font-bold uppercase
9. WHEN "Export" is clicked, THE Daily_Close_View SHALL trigger report generation
10. THE Daily_Close_View SHALL handle empty data with "No closes found" message in text-slate-400

### Requirement 8: Backend API Extension for Daily Closes

**User Story:** Como desarrollador frontend, necesito que el backend soporte cierres diarios con comparación de fechas específicas, para implementar la funcionalidad de cierre diario en el frontend.

#### Acceptance Criteria

1. THE Backend_API SHALL provide a new endpoint POST /api/counters/close-day for daily closes
2. THE Backend_API SHALL accept parameters: printer_id, close_date, closed_by, notes
3. WHEN close-day is called, THE Backend_API SHALL read counters for the specified date
4. THE Backend_API SHALL calculate comparison date as same day of previous month (e.g., March 2 → February 2)
5. THE Backend_API SHALL fetch counters for comparison date
6. THE Backend_API SHALL calculate differences between close_date and comparison_date
7. THE Backend_API SHALL return close record with: counters, comparison_counters, differences, comparison_date
8. IF counters for close_date do not exist, THE Backend_API SHALL return 404 error
9. IF counters for comparison_date do not exist, THE Backend_API SHALL return close with null comparison values
10. THE Backend_API SHALL provide endpoint GET /api/counters/closes/daily with optional date range filters
11. THE Backend_API SHALL provide endpoint GET /api/counters/closes/daily/{id} for specific daily close
12. THE Backend_API SHALL prevent duplicate closes for same printer and date combination
13. FOR ALL daily closes, differences SHALL equal close_date counters minus comparison_date counters (invariant property)

**Note:** This requirement identifies a backend limitation that must be addressed. The existing /api/counters/close-month endpoint only supports monthly closes (entire month comparison). The frontend implementation depends on this backend enhancement.

### Requirement 9: Export Functionality

**User Story:** Como usuario, quiero exportar reportes de contadores a Excel y PDF, para compartir información con otros departamentos.

#### Acceptance Criteria

1. THE Export_Service SHALL provide a function to export counter data to Excel format using a library (xlsx or similar)
2. THE Export_Service SHALL provide a function to export daily close report to PDF format using a library (jspdf or similar)
3. WHEN exporting to Excel, THE Export_Service SHALL include all counter fields
4. WHEN exporting to Excel, THE Export_Service SHALL include user counter breakdown
5. WHEN exporting to PDF, THE Export_Service SHALL include printer identification
6. WHEN exporting to PDF, THE Export_Service SHALL include daily close summary with comparison date
7. WHEN exporting to PDF, THE Export_Service SHALL include difference calculations
8. WHEN export completes, THE Export_Service SHALL trigger browser download
9. IF export fails, THE Export_Service SHALL throw error with descriptive message
10. THE Export_Service SHALL generate filenames with format: "counters_{printer}_{date}.xlsx"
11. THE Export_Service SHALL generate PDF filenames with format: "close_{printer}_{date}.pdf"
12. THE Export button SHALL be styled with text-xs font-bold uppercase tracking-wide

### Requirement 9: Loading States and Feedback

**User Story:** Como usuario, quiero ver indicadores visuales durante operaciones largas, para saber que el sistema está procesando mi solicitud.

#### Acceptance Criteria

1. THE Loading_Indicator SHALL display Loader2 icon from lucide-react with animate-spin class
2. THE Loading_Indicator SHALL display descriptive text in text-slate-400 (e.g., "Reading counters...")
3. WHILE reading a single printer, THE Loading_Indicator SHALL display "Reading printer {hostname}..."
4. WHILE reading all printers, THE Loading_Indicator SHALL display "Reading all printers..."
5. WHILE performing daily close, THE Loading_Indicator SHALL display "Processing daily close..."
6. WHILE exporting data, THE Loading_Indicator SHALL display "Generating export..."
7. THE Loading_Indicator SHALL disable user interaction with underlying components using disabled:opacity-50 disabled:cursor-not-allowed
8. WHEN operation completes, THE Loading_Indicator SHALL hide automatically
9. IF operation takes more than 30 seconds, THE Loading_Indicator SHALL display "This may take a while..." in text-sm

### Requirement 10: Error Handling and Messages

**User Story:** Como usuario, quiero ver mensajes de error claros cuando algo falla, para entender qué salió mal y cómo resolverlo.

#### Acceptance Criteria

1. THE Error_Handler SHALL display error messages in a visible notification with bg-error/10 border-error
2. THE Error_Handler SHALL display error icon from lucide-react with text-error
3. THE Error_Handler SHALL display error title and detailed message in text-sm
4. WHEN API returns 404, THE Error_Handler SHALL display "Resource not found"
5. WHEN API returns 400, THE Error_Handler SHALL display validation error details
6. WHEN API returns 500, THE Error_Handler SHALL display "Server error, please try again"
7. WHEN network fails, THE Error_Handler SHALL display "Connection error, check network"
8. THE Error_Handler SHALL provide a "Dismiss" button styled with text-xs font-bold uppercase
9. WHEN "Dismiss" is clicked, THE Error_Handler SHALL hide the notification
10. THE Error_Handler SHALL auto-dismiss after 10 seconds for non-critical errors
11. THE Error_Handler SHALL remain visible until dismissed for critical errors

### Requirement 11: Navigation and Routing

**User Story:** Como usuario, quiero navegar entre diferentes vistas del módulo de contadores, para acceder a la funcionalidad que necesito.

#### Acceptance Criteria

1. THE Counter_Module SHALL integrate with existing App navigation menu in App.tsx
2. THE Counter_Module SHALL add a "Contadores" menu item with icon from lucide-react styled with existing nav button patterns
3. WHEN "Contadores" menu item is clicked, THE Counter_Module SHALL display Dashboard_View
4. THE Counter_Module SHALL use state-based navigation matching existing pattern (vistaActual state)
5. THE Counter_Module SHALL support views: dashboard, printer-detail, daily-close
6. WHEN navigating to invalid printer ID, THE Counter_Module SHALL display 404 error
7. THE Counter_Module navigation button SHALL use bg-ricoh-red when active, text-slate-300 hover:bg-slate-800 when inactive
8. THE Counter_Module navigation button SHALL include border-l-4 border-white when active
9. THE Counter_Module SHALL use text-sm font-bold uppercase tracking-wide for menu items

### Requirement 12: Responsive Design

**User Story:** Como usuario, quiero usar el módulo de contadores en diferentes dispositivos, para acceder desde desktop o tablet.

#### Acceptance Criteria

1. THE Counter_Module SHALL be fully functional on desktop viewports (min-width: 1024px)
2. THE Counter_Module SHALL be fully functional on tablet viewports (min-width: 768px)
3. WHEN viewport width is less than 1024px, THE Counter_Module SHALL adjust layout to single column
4. WHEN viewport width is less than 768px, THE Counter_Module SHALL display "Use desktop or tablet" message in text-slate-400
5. THE User_Counter_Table SHALL enable horizontal scrolling on narrow viewports using overflow-x-auto
6. THE History_Chart SHALL scale proportionally to container width
7. THE Dashboard_View SHALL display printer cards in responsive grid (1-3 columns based on width) using grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3
8. THE Counter_Module SHALL use existing responsive patterns from AdministracionUsuarios component

### Requirement 13: Data Refresh and Caching

**User Story:** Como usuario, quiero que los datos se actualicen automáticamente, para ver información reciente sin recargar manualmente.

#### Acceptance Criteria

1. THE Dashboard_View SHALL refresh printer list every 60 seconds using useEffect with interval
2. THE Printer_Detail_View SHALL refresh counter data every 30 seconds using useEffect with interval
3. WHEN manual refresh is triggered, THE Counter_Module SHALL invalidate cached data
4. THE Counter_Module MAY use Zustand store for state management (matching existing pattern in usuarios module)
5. WHEN cached data exists and is fresh, THE Counter_Module SHALL use cached data
6. WHEN cached data is stale, THE Counter_Module SHALL fetch new data
7. WHEN user navigates away and returns, THE Counter_Module SHALL check cache freshness
8. THE Counter_Module SHALL provide manual refresh button styled with RefreshCw icon from lucide-react

### Requirement 14: Accessibility

**User Story:** Como usuario con necesidades de accesibilidad, quiero usar el módulo de contadores con tecnologías asistivas, para acceder a toda la funcionalidad.

#### Acceptance Criteria

1. THE Counter_Module SHALL provide ARIA labels for all interactive elements
2. THE Counter_Module SHALL support keyboard navigation (Tab, Enter, Escape)
3. THE Counter_Module SHALL provide focus indicators using focus:outline-none focus:ring-2 focus:ring-ricoh-red
4. THE History_Chart SHALL provide text alternative describing data trends
5. THE User_Counter_Table SHALL provide sortable column headers with ARIA sort attributes
6. THE Loading_Indicator SHALL announce loading state to screen readers
7. THE Error_Handler SHALL announce errors to screen readers with role="alert"
8. THE Counter_Module SHALL maintain color contrast ratio of at least 4.5:1 using existing color palette
9. THE Counter_Module SHALL not rely solely on color to convey information

### Requirement 15: Performance

**User Story:** Como usuario, quiero que el módulo de contadores cargue rápidamente, para trabajar eficientemente.

#### Acceptance Criteria

1. WHEN Dashboard_View loads, THE Counter_Module SHALL display initial content within 2 seconds
2. WHEN Printer_Detail_View loads, THE Counter_Module SHALL display counter data within 2 seconds
3. WHEN History_Chart renders, THE Counter_Module SHALL display chart within 1 second
4. WHEN User_Counter_Table renders with 500 users, THE Counter_Module SHALL display table within 2 seconds using pagination (50 items per page)
5. THE Counter_Module SHALL lazy-load chart library (recharts) only when History_Chart is displayed
6. THE Counter_Module SHALL debounce filter inputs with 300ms delay
7. THE Counter_Module MAY virtualize User_Counter_Table for more than 100 users (optional optimization)
8. THE Counter_Module SHALL optimize re-renders using React.memo for static components
9. THE Counter_Module SHALL use existing pagination pattern from AdministracionUsuarios (50 items per page)
