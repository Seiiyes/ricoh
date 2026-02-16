# Implementation Plan: Remove Static Data

## Overview

This implementation plan breaks down the removal of static mock data into incremental steps. Each task builds on previous work, starting with store enhancements, then creating the API service layer, updating components, and finally adding proper state handling. The approach ensures the application remains functional at each checkpoint.

## Tasks

- [ ] 1. Enhance Zustand store with printer data management
  - [x] 1.1 Add printer state fields to store interface
    - Add `printers: PrinterDevice[]` field (initially empty array)
    - Add `isLoading: boolean` field (initially false)
    - Update store type definitions
    - _Requirements: 2.1, 3.1_
  
  - [x] 1.2 Implement setPrinters method
    - Create method that accepts `PrinterDevice[]` and updates store
    - Ensure method replaces entire printers array
    - _Requirements: 2.2_
  
  - [x] 1.3 Implement clearPrinters method
    - Create method that sets printers to empty array
    - _Requirements: 2.4_
  
  - [x] 1.4 Implement setLoading method
    - Create method that accepts boolean and updates isLoading state
    - _Requirements: 3.2_
  
  - [x] 1.5 Write property test for store printer data round-trip
    - **Property 1: Store Printer Data Round-Trip**
    - **Validates: Requirements 2.2, 2.3**
  
  - [x] 1.6 Write property test for clearPrinters
    - **Property 2: Clear Printers Results in Empty State**
    - **Validates: Requirements 2.4**
  
  - [x] 1.7 Write property test for setLoading
    - **Property 3: Loading State Updates Correctly**
    - **Validates: Requirements 3.2**

- [ ] 2. Create API service layer structure
  - [x] 2.1 Create printerService module
    - Create `src/services/printerService.ts` file
    - Define `fetchPrinters` function with `Promise<PrinterDevice[]>` return type
    - Implement placeholder that returns empty array
    - Add TODO comments for future API integration
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 2.2 Write unit test for API service placeholder
    - Test that fetchPrinters returns empty array
    - Test that return type matches PrinterDevice[]
    - _Requirements: 5.4_

- [ ] 3. Create data transformation utilities
  - [x] 3.1 Create transformation utility module
    - Create `src/utils/printerTransform.ts` file
    - Implement `printerDeviceToCardProps` function
    - Map PrinterDevice fields to PrinterCardProps format
    - Handle toner_levels to toner format conversion
    - _Requirements: 6.3_
  
  - [x] 3.2 Write unit tests for transformation with missing fields
    - Test transformation provides defaults for missing status
    - Test transformation provides defaults for missing toner_levels
    - _Requirements: Error Handling_
  
  - [x] 3.3 Write property test for transformation preserves fields
    - Test that all valid PrinterDevice fields are preserved in transformation
    - _Requirements: 6.3_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Update ProvisioningPanel component
  - [x] 5.1 Remove mockPrinters array
    - Delete the local mockPrinters constant
    - _Requirements: 1.1_
  
  - [x] 5.2 Connect component to store
    - Import and use `printers` and `isLoading` from usePrinterStore
    - Remove local mock data references
    - _Requirements: 1.2_
  
  - [x] 5.3 Implement loading state UI
    - Add conditional rendering for loading state
    - Create simple loading spinner or message
    - Show loading UI when `isLoading === true`
    - _Requirements: 3.3_
  
  - [x] 5.4 Implement empty state UI
    - Add conditional rendering for empty state
    - Create empty state message component
    - Show when `printers.length === 0 && !isLoading`
    - Include message "No printers currently available"
    - _Requirements: 4.1, 4.2_
  
  - [x] 5.5 Update printer grid to use store data
    - Map over `printers` from store instead of mockPrinters
    - Use transformation utility to convert to PrinterCard props
    - Maintain existing grid layout
    - _Requirements: 7.4_
  
  - [x] 5.6 Write unit test for loading state rendering
    - Test that loading indicator appears when isLoading is true
    - _Requirements: 3.3_
  
  - [x] 5.7 Write unit test for empty state rendering
    - Test that empty state appears when printers array is empty and not loading
    - Test that empty state message is present
    - _Requirements: 4.1, 4.2_
  
  - [x] 5.8 Write unit test for form and console presence
    - Test that user provisioning form is still rendered
    - Test that live console is still rendered
    - _Requirements: 7.2, 7.3_

- [ ] 6. Update PrinterCard component for dynamic data
  - [x] 6.1 Verify PrinterCard works with transformed data
    - Ensure component receives correct props from transformation
    - Test with empty printers array from store
    - _Requirements: 7.1_
  
  - [x] 6.2 Write property test for PrinterCard rendering
    - **Property 4: PrinterCard Renders All Required Fields**
    - **Validates: Requirements 7.1**

- [ ] 7. Integrate printer selection with dynamic data
  - [x] 7.1 Verify togglePrinter works with store printer IDs
    - Test that selection works when printers come from store
    - Ensure selected state persists correctly
    - _Requirements: 7.5_
  
  - [x] 7.2 Write property test for printer selection
    - **Property 5: Printer Selection Works With Dynamic Data**
    - **Validates: Requirements 7.5**

- [ ] 8. Add initialization hook for future API calls
  - [x] 8.1 Create useEffect hook in ProvisioningPanel
    - Add useEffect that runs on component mount
    - Call setLoading(true) before API call
    - Call printerService.fetchPrinters()
    - Call setPrinters with result
    - Call setLoading(false) after completion
    - Add error handling structure (log errors for now)
    - _Requirements: 5.5_
  
  - [x] 8.2 Write integration test for API to store flow
    - Test that calling fetchPrinters updates store correctly
    - Test that loading state transitions properly
    - _Requirements: 5.5_

- [x] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The mockPrinters array is removed in task 5.1, after store infrastructure is ready
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples, edge cases, and integration points
- All changes maintain TypeScript type safety throughout
