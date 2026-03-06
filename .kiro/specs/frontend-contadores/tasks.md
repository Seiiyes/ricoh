# Implementation Plan: Frontend Contadores

## Overview

This implementation plan breaks down the frontend counter module into discrete coding tasks with CRITICAL UPDATES for daily close functionality. The module provides a comprehensive interface for viewing, querying, and managing printer counters through a React-based web application.

**CRITICAL CHANGES FROM INITIAL PLAN:**
1. **Backend API First**: New endpoints for daily closes must be implemented before frontend
2. **Daily Closes (Not Monthly)**: Users select specific dates, system compares with same day of previous month
3. **User Counter Table**: Already implemented but not displaying data - needs debugging
4. **Completed Work**: Types, counterService, Dashboard, Detail views, and UserCounterTable are done

The implementation uses TypeScript, React 19, Tailwind CSS, and integrates with the backend API (9 existing + 3 new endpoints for daily closes).

## Tasks

- [x] 1. Install dependencies and set up project structure
  - Install required npm packages: recharts, xlsx, jspdf, jspdf-autotable, fast-check
  - Create directory structure: components/contadores/{dashboard,detail,daily,shared}, services/, types/
  - _Requirements: 1.1-1.12_
  - **Status: COMPLETED**

- [x] 2. Define TypeScript types and interfaces
  - [x] 2.1 Create counter type definitions
    - Create src/types/counter.ts with all interfaces: TotalCounter, UserCounter, DailyClose, DailyCloseRequest, ReadResult, ReadAllResult
    - Include all counter fields matching backend API response structure
    - _Requirements: 1.12_
    - **Status: COMPLETED**

- [ ] 3. Implement Backend API for Daily Closes (BLOCKING)
  - [ ] 3.1 Create daily_closes database table
    - Create migration for daily_closes table with fields: id, printer_id, close_date, comparison_date, totals, differences, fecha_cierre, cerrado_por, notas
    - Add UNIQUE constraint on (printer_id, close_date)
    - _Requirements: 8.1-8.13_
  
  - [ ] 3.2 Implement POST /api/counters/close-day endpoint
    - Accept parameters: printer_id, close_date, cerrado_por, notas
    - Read counters for close_date
    - Calculate comparison_date (same day of previous month)
    - Fetch counters for comparison_date
    - Calculate differences (close_date - comparison_date)
    - Return DailyClose object with comparison_date and differences
    - Handle duplicate close error (409)
    - Handle missing counters error (404)
    - _Requirements: 6.1-6.10, 8.1-8.13_
  
  - [ ] 3.3 Implement GET /api/counters/closes/daily endpoint
    - Accept query parameters: printer_id (required), start_date, end_date
    - Return array of DailyClose objects
    - Order by close_date DESC
    - _Requirements: 7.1-7.7, 8.10_
  
  - [ ] 3.4 Implement GET /api/counters/closes/daily/{id} endpoint
    - Return single DailyClose object by ID
    - Return 404 if not found
    - _Requirements: 8.11_

- [x] 4. Implement Counter Service Layer
  - [x] 4.1 Create counterService.ts with API integration
    - Implement fetchLatestCounter() function
    - Implement fetchCounterHistory() with optional date filters
    - Implement fetchUserCounters() function
    - Implement triggerManualRead() function
    - Implement triggerReadAll() function
    - Use API_BASE_URL from environment variables
    - Add error handling with descriptive messages for all functions
    - _Requirements: 1.1-1.9_
    - **Status: COMPLETED**
  
  - [ ] 4.2 Update counterService for daily closes
    - Implement performDailyClose() function (calls POST /api/counters/close-day)
    - Implement fetchDailyCloses() with optional date range filters
    - Implement fetchDailyClose() for specific close
    - Add error handling for duplicate close and missing counters
    - _Requirements: 6.1-6.10, 7.1-7.7_
  
  - [ ]* 4.3 Write unit tests for counterService
    - Test successful API calls with mocked responses
    - Test error handling for 404, 400, 500 status codes
    - Test network error handling
    - Test query parameter construction for filters
    - _Requirements: 1.10_
  
  - [ ]* 4.4 Write property test for API error handling
    - **Property 1: API Error Handling**
    - **Validates: Requirements 1.10**
    - Test that any HTTP error status (400-599) throws an Error
    - Use fast-check to generate random status codes and error messages

- [x] 5. Implement shared components
  - [x] 5.1 Create LoadingIndicator component
    - Create src/components/contadores/shared/LoadingIndicator.tsx
    - Use Loader2 icon from lucide-react with animate-spin
    - Accept optional message prop
    - _Requirements: 2.9, 3.7_
    - **Status: COMPLETED**
  
  - [x] 5.2 Create ErrorHandler component
    - Create src/components/contadores/shared/ErrorHandler.tsx
    - Display error message with AlertCircle icon
    - Include dismiss button
    - Auto-dismiss after 10s for non-critical errors
    - _Requirements: 2.11, 3.9_
    - **Status: COMPLETED**
  
  - [x] 5.3 Create PrinterCounterCard component
    - Create src/components/contadores/dashboard/PrinterCounterCard.tsx
    - Display printer hostname, IP address, location
    - Display total counter value and last reading timestamp
    - Use existing card styling (bg-white, rounded-lg, shadow-sm, border-slate-200)
    - Add hover effect and cursor-pointer
    - Accept onClick handler for navigation
    - _Requirements: 2.1, 2.3-2.6_
    - **Status: COMPLETED**

- [ ] 6. Debug User Counter Display Issue (QUICK WIN)
  - [ ] 6.1 Investigate why UserCounterTable is not showing data
    - Check if fetchUserCounters() is being called correctly in PrinterDetailView
    - Verify API endpoint /api/counters/users/{printer_id} returns data
    - Check if userCounters state is being populated
    - Verify table rendering logic and conditional rendering
    - Check for console errors or warnings
    - _Requirements: 5.1-5.14_
  
  - [ ] 6.2 Fix UserCounterTable data display
    - Apply fix based on investigation findings
    - Test with real printer data
    - Verify sorting, filtering, and pagination work correctly
    - _Requirements: 5.1-5.14_

- [ ] 7. Checkpoint - Verify foundation and quick wins
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement Dashboard View
  - [x] 8.1 Create DashboardView component
    - Create src/components/contadores/dashboard/DashboardView.tsx
    - Fetch printers using printerService on mount
    - Fetch latest counter for each printer using fetchLatestCounter()
    - Render PrinterCounterCard for each printer
    - Implement "Read All Printers" button with ricoh-red styling
    - Handle card click to navigate to printer detail
    - Display LoadingIndicator while fetching data
    - Display ErrorHandler for API errors
    - Add auto-refresh every 60 seconds
    - Use Tailwind classes consistent with existing components
    - _Requirements: 2.1-2.13_
    - **Status: COMPLETED**
  
  - [ ]* 8.2 Write unit tests for DashboardView
    - Test printer card rendering for multiple printers
    - Test loading state display
    - Test empty printer list handling
    - Test error state display
    - Test "Read All" button click
    - _Requirements: 2.1-2.13_
  
  - [ ]* 8.3 Write property test for printer card rendering
    - **Property 4: Printer Card Rendering**
    - **Validates: Requirements 2.1, 2.3, 2.4, 2.5**
    - Test that any non-empty array of printers renders exactly one card per printer
    - Verify each card displays hostname, ip_address, and location

- [x] 9. Implement Counter Breakdown component
  - [x] 9.1 Create CounterBreakdown component
    - Create src/components/contadores/detail/CounterBreakdown.tsx
    - Display counters grouped by function: copiadora, impresora, escaner, fax
    - Show B/N and Color counters for each function
    - Use card layout with bg-white, rounded-lg, shadow-sm
    - Format numbers with toLocaleString()
    - _Requirements: 3.2, 3.3_
    - **Status: COMPLETED**

- [x] 10. Implement History Chart component
  - [x] 10.1 Create HistoryChart component with lazy loading
    - Create src/components/contadores/detail/HistoryChart.tsx
    - Lazy-load recharts library using React.lazy
    - Display LineChart with total, copiadora, impresora, escaner lines
    - Implement date range filter buttons: 7d, 30d, 90d, all
    - Filter history data based on selected range
    - Use ricoh-red for total line, distinct colors for functions
    - Show "No hay datos disponibles" for empty data
    - Wrap chart in Suspense with LoadingIndicator fallback
    - _Requirements: 4.1-4.9_
    - **Status: COMPLETED**

- [x] 11. Implement User Counter Table component
  - [x] 11.1 Create UserCounterTable component
    - Create src/components/contadores/detail/UserCounterTable.tsx
    - Display user counters in table with columns: código, nombre, total, B/N, color
    - Implement search filter by user code or name
    - Implement sortable columns (click header to sort)
    - Implement pagination at 50 items per page
    - Show pagination controls with current page and total pages
    - Use existing table styling patterns
    - _Requirements: 5.1-5.11_
    - **Status: COMPLETED (but not displaying data - see task 6)**
  
  - [ ]* 11.2 Write unit tests for UserCounterTable
    - Test search filtering functionality
    - Test column sorting (ascending/descending)
    - Test pagination controls
    - Test empty state display
    - _Requirements: 5.1-5.11_

- [x] 12. Implement Printer Detail View
  - [x] 12.1 Create PrinterIdentification component
    - Create src/components/contadores/detail/PrinterIdentification.tsx
    - Display printer hostname, IP address, serial number
    - Display last reading timestamp
    - Use card layout with existing styling
    - _Requirements: 3.1, 3.4_
    - **Status: COMPLETED**
  
  - [x] 12.2 Create PrinterDetailView component
    - Create src/components/contadores/detail/PrinterDetailView.tsx
    - Accept printerId prop and onNavigateBack callback
    - Fetch printer data, latest counter, history, and user counters on mount
    - Render PrinterIdentification, CounterBreakdown, HistoryChart, UserCounterTable
    - Implement "Manual Read" button with ricoh-red styling
    - Handle manual read with loading state and error handling
    - Add auto-refresh every 30 seconds
    - Implement back button navigation
    - _Requirements: 3.1-3.12_
    - **Status: COMPLETED**
  
  - [ ]* 12.3 Write unit tests for PrinterDetailView
    - Test component rendering with valid printer ID
    - Test manual read button functionality
    - Test loading states
    - Test error handling
    - Test back navigation
    - _Requirements: 3.1-3.12_

- [ ] 13. Checkpoint - Verify dashboard and detail views
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement Daily Close components
  - [ ] 14.1 Create CloseForm component
    - Create src/components/contadores/daily/CloseForm.tsx
    - Implement printer select dropdown
    - Implement date picker for specific date selection (e.g., March 2, 2026)
    - Implement optional "cerrado_por" text input
    - Implement optional notes textarea
    - Add form validation: date <= current date
    - Display validation errors inline
    - Handle form submission with loading state
    - Show helper text: "Se comparará con el mismo día del mes anterior"
    - _Requirements: 6.1-6.10_
  
  - [ ] 14.2 Create CloseHistoryTable component
    - Create src/components/contadores/daily/CloseHistoryTable.tsx
    - Display daily closes in table with columns: fecha, fecha comparación, total, diferencias, cerrado por
    - Implement date range filter (start_date, end_date)
    - Add export button per row to generate PDF
    - Use existing table styling patterns
    - Display comparison date for each close (e.g., "vs Feb 2, 2026")
    - _Requirements: 7.1-7.7_
  
  - [ ] 14.3 Create DailyCloseView component
    - Create src/components/contadores/daily/DailyCloseView.tsx
    - Render CloseForm and CloseHistoryTable
    - Fetch printers on mount
    - Fetch closes when printer or date range filter changes
    - Handle close form submission
    - Display success message with comparison date and differences after close
    - Handle duplicate close error (409 conflict)
    - Handle no counters error
    - _Requirements: 6.1-6.10, 7.1-7.7_
  
  - [ ]* 14.4 Write unit tests for daily close validation
    - Test future date rejection
    - Test duplicate close error handling
    - Test no counters error handling
    - _Requirements: 6.6-6.10_

- [ ] 15. Implement Export Service
  - [ ] 15.1 Create exportService.ts
    - Create src/services/exportService.ts
    - Implement exportToExcel() function using xlsx library
    - Create two sheets: "Contadores Totales" and "Contadores por Usuario"
    - Format data with proper headers and values
    - Generate filename with printer name and date
    - Implement exportDailyCloseToPDF() function using jspdf
    - Create PDF with printer info, close date, comparison date, counter table, and notes
    - Use jspdf-autotable for table formatting
    - Generate filename with printer name and date
    - _Requirements: 9.1-9.12_
  
  - [ ] 15.2 Integrate export buttons in UI
    - Add export button to CloseHistoryTable rows
    - Call exportDailyCloseToPDF() on button click
    - Add export button to PrinterDetailView (optional enhancement)
    - _Requirements: 9.1-9.12_
  
  - [ ]* 15.3 Write unit tests for exportService
    - Test Excel workbook generation
    - Test PDF document generation
    - Test filename formatting
    - Mock xlsx and jspdf libraries
    - _Requirements: 9.1-9.12_

- [ ] 16. Implement main module component and navigation
  - [ ] 16.1 Create ContadoresModule component
    - Create src/components/contadores/ContadoresModule.tsx
    - Manage internal navigation state: 'dashboard' | 'printer-detail' | 'daily-close'
    - Track selectedPrinterId for detail view
    - Implement navigation handlers: onNavigateToPrinter, onNavigateBack, onNavigateToDailyClose
    - Render appropriate view based on current state
    - _Requirements: 2.1-2.13, 3.1-3.12, 6.1-6.10_
  
  - [ ] 16.2 Integrate ContadoresModule into App.tsx
    - Add "Contadores" menu item to navigation with BarChart3 icon
    - Add 'contadores' to vistaActual type union
    - Render ContadoresModule when vistaActual === 'contadores'
    - Use existing navigation styling patterns
    - _Requirements: 2.1-2.13_

- [ ] 17. Checkpoint - Verify complete module integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 18. Implement property-based tests for data invariants
  - [ ]* 18.1 Write property test for total counter invariant
    - **Property 2: Total Counter Invariant**
    - **Validates: Requirements 4.9**
    - Test that sum of function counters <= total for any TotalCounter
    - Use fast-check to generate random counter objects
  
  - [ ]* 18.2 Write property test for user counter invariant
    - **Property 3: User Counter Invariant**
    - **Validates: Requirements 5.10**
    - Test that total_paginas = total_bn + total_color for any UserCounter
    - Use fast-check to generate random user counter objects
  
  - [ ]* 18.3 Write property test for navigation behavior
    - **Property 5: Navigation on Card Click**
    - **Validates: Requirements 2.6**
    - Test that clicking any printer card navigates to detail view with correct printer ID

- [ ] 19. Add accessibility features
  - [ ] 19.1 Add ARIA labels to interactive elements
    - Add aria-label to all buttons without visible text
    - Add aria-label to search inputs
    - Add aria-label to select dropdowns
    - Add role="alert" to error messages
    - Add aria-live="polite" to loading indicators
    - _Requirements: 14.1-14.9_
  
  - [ ] 19.2 Implement keyboard navigation
    - Ensure all interactive elements are keyboard accessible
    - Add visible focus indicators
    - Test Tab navigation through all views
    - Test Enter key activation for buttons
    - Test Escape key for dismissing errors
    - _Requirements: 14.1-14.9_

- [ ] 20. Performance optimizations
  - [ ] 20.1 Add React.memo to static components
    - Memoize PrinterCounterCard component
    - Memoize CounterBreakdown component
    - Memoize table row components
    - _Requirements: 15.1-15.9_
  
  - [ ] 20.2 Add useMemo for expensive computations
    - Memoize sorted user counter arrays
    - Memoize filtered user counter arrays
    - Memoize chart data transformations
    - _Requirements: 15.1-15.9_
  
  - [ ] 20.3 Verify lazy loading implementation
    - Confirm recharts is lazy-loaded
    - Confirm export libraries are only loaded when needed
    - Verify Suspense boundaries are in place
    - _Requirements: 15.1-15.9_

- [ ] 21. Final testing and polish
  - [ ]* 21.1 Run complete test suite
    - Execute all unit tests
    - Execute all property-based tests
    - Verify test coverage meets goals (service: 90%, components: 80%)
    - Fix any failing tests
  
  - [ ] 21.2 Manual end-to-end testing
    - Test complete user flow: dashboard → detail → daily close
    - Test all error scenarios
    - Test all loading states
    - Test responsive design on different screen sizes
    - Test with real backend API
  
  - [ ] 21.3 Code review and cleanup
    - Remove console.log statements
    - Remove commented-out code
    - Verify consistent code formatting
    - Verify all TypeScript types are properly defined
    - Check for any remaining 'any' types

- [ ] 22. Final checkpoint - Production readiness
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- The implementation follows the 6-phase plan from the design document
- Property-based tests use fast-check library with minimum 100 iterations
- All components use TypeScript with strict type checking
- Styling follows existing Tailwind patterns for consistency
- Auto-refresh intervals: 60s for dashboard, 30s for detail view
- Pagination set to 50 items per page matching existing patterns
- **CRITICAL**: Backend API tasks (3.1-3.4) must be completed before daily close frontend tasks (14.1-14.3)
- **PRIORITY**: Debug user counter display (task 6) is a quick win that should be addressed early
