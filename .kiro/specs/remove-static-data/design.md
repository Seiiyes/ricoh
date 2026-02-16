# Design Document: Remove Static Data

## Overview

This design outlines the approach for removing hardcoded mock printer data from the frontend application and preparing it for dynamic data consumption from backend APIs. The solution focuses on centralizing data management in the Zustand store, implementing proper loading and empty states, and creating a clean API integration layer.

The design maintains backward compatibility with existing components while establishing patterns that support future API integration. All changes preserve TypeScript type safety and the existing UI/UX.

## Architecture

### Current Architecture
```
ProvisioningPanel (Component)
  └─> mockPrinters (local array) ──> PrinterCard (Component)
  └─> usePrinterStore (logs, selection only)
```

### Target Architecture
```
API Service Layer (placeholder functions)
  └─> usePrinterStore (centralized state)
      ├─> printers: PrinterDevice[]
      ├─> isLoading: boolean
      └─> methods: setPrinters, clearPrinters, setLoading
          └─> ProvisioningPanel (Component)
              └─> PrinterCard (Component)
```

### Key Architectural Changes

1. **Centralized State Management**: Move printer data from component-local state to Zustand store
2. **API Service Layer**: Create a dedicated service module for future API calls
3. **State-Driven UI**: Components react to store state changes (loading, empty, populated)
4. **Separation of Concerns**: Clear boundaries between data fetching, state management, and presentation

## Components and Interfaces

### 1. Enhanced Printer Store

**Location**: `src/store/usePrinterStore.ts`

**Extended Interface**:
```typescript
interface PrinterStore {
  // Existing
  selectedPrinters: string[];
  logs: Log[];
  togglePrinter: (id: string) => void;
  addLog: (message: string, type?: Log['type']) => void;
  clearSelection: () => void;
  
  // New additions
  printers: PrinterDevice[];
  isLoading: boolean;
  setPrinters: (printers: PrinterDevice[]) => void;
  clearPrinters: () => void;
  setLoading: (loading: boolean) => void;
}
```

**Responsibilities**:
- Store the collection of printer devices
- Manage loading state for async operations
- Provide methods to update printer data
- Maintain existing selection and logging functionality

**State Management**:
- `printers`: Array of PrinterDevice objects (initially empty)
- `isLoading`: Boolean flag for loading state (initially false)
- State updates trigger re-renders in consuming components

### 2. API Service Layer

**Location**: `src/services/printerService.ts` (new file)

**Interface**:
```typescript
interface PrinterService {
  fetchPrinters: () => Promise<PrinterDevice[]>;
  fetchPrinterById: (id: string) => Promise<PrinterDevice>;
}
```

**Implementation Strategy**:
- Create placeholder functions that return empty arrays or mock data
- Use proper async/await patterns
- Include error handling structure
- Type all return values with PrinterDevice interface
- Add comments indicating where actual API calls will be implemented

**Example Structure**:
```typescript
export const printerService = {
  fetchPrinters: async (): Promise<PrinterDevice[]> => {
    // TODO: Replace with actual API call
    // const response = await fetch('/api/printers');
    // return response.json();
    
    // Placeholder: return empty array
    return [];
  }
};
```

### 3. Updated ProvisioningPanel Component

**Location**: `src/components/governance/ProvisioningPanel.tsx`

**Changes**:
- Remove `mockPrinters` local array
- Consume `printers`, `isLoading` from store
- Implement conditional rendering for loading/empty/populated states
- Maintain all existing UI elements (form, console, search)

**Rendering Logic**:
```typescript
if (isLoading) {
  return <LoadingSpinner />;
}

if (printers.length === 0) {
  return <EmptyState />;
}

return <PrinterGrid printers={printers} />;
```

### 4. Data Transformation Layer

**Location**: `src/utils/printerTransform.ts` (new file)

**Purpose**: Transform API response data to match internal PrinterDevice interface

**Interface**:
```typescript
interface PrinterTransform {
  apiToPrinterDevice: (apiData: any) => PrinterDevice;
  printerCardProps: (device: PrinterDevice) => PrinterCardProps;
}
```

**Responsibilities**:
- Map API response fields to PrinterDevice interface
- Transform printer device data to PrinterCard component props
- Handle missing or malformed data gracefully
- Provide default values for optional fields

## Data Models

### Existing PrinterDevice Interface
```typescript
interface PrinterDevice {
  id: string;
  hostname: string;
  ip_address: string;
  status: 'online' | 'offline';
  toner_levels: { cyan: number; magenta: number; yellow: number; black: number };
  capabilities: { color: boolean; scanner: boolean };
}
```

**Usage**: This interface remains unchanged and serves as the canonical type for printer data throughout the application.

### PrinterCard Props Mapping

**Current Props**:
```typescript
interface PrinterCardProps {
  id: string;
  name: string;      // Maps to: hostname
  ip: string;        // Maps to: ip_address
  status: 'online' | 'offline';
  toner: { c: number; m: number; y: number; k: number };  // Maps to: toner_levels
}
```

**Transformation Function**:
```typescript
function printerDeviceToCardProps(device: PrinterDevice): PrinterCardProps {
  return {
    id: device.id,
    name: device.hostname,
    ip: device.ip_address,
    status: device.status,
    toner: {
      c: device.toner_levels.cyan,
      m: device.toner_levels.magenta,
      y: device.toner_levels.yellow,
      k: device.toner_levels.black
    }
  };
}
```

### Store State Shape

```typescript
{
  // Printer data
  printers: PrinterDevice[],           // Empty array initially
  isLoading: boolean,                  // false initially
  
  // Existing state
  selectedPrinters: string[],
  logs: Log[]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Store Printer Data Round-Trip

*For any* array of valid PrinterDevice objects, setting the printers in the store and then retrieving them should return an equivalent array with all printer data intact.

**Validates: Requirements 2.2, 2.3**

### Property 2: Clear Printers Results in Empty State

*For any* initial printer collection in the store, calling clearPrinters should result in an empty printers array.

**Validates: Requirements 2.4**

### Property 3: Loading State Updates Correctly

*For any* boolean value (true or false), calling setLoading with that value should update the isLoading state to match the provided value.

**Validates: Requirements 3.2**

### Property 4: PrinterCard Renders All Required Fields

*For any* valid PrinterDevice object, the PrinterCard component should render output that contains the printer's name (hostname), IP address, status, and all four toner level values (cyan, magenta, yellow, black).

**Validates: Requirements 7.1**

### Property 5: Printer Selection Works With Dynamic Data

*For any* printer ID from the current printer collection, calling togglePrinter with that ID should correctly add it to selectedPrinters if not present, or remove it if already present.

**Validates: Requirements 7.5**

## Error Handling

### Store Operations

**Invalid Data Handling**:
- `setPrinters`: Accept only arrays; if non-array is passed, log error and maintain current state
- `togglePrinter`: If printer ID doesn't exist in current collection, log warning but don't throw error
- All store methods should be defensive and never throw exceptions that crash the app

**Type Safety**:
- TypeScript will enforce PrinterDevice interface at compile time
- Runtime validation is not required for internal store operations
- API layer should validate data before passing to store

### Component Rendering

**Loading State**:
- If `isLoading` is true, show loading spinner regardless of printer data
- Loading state takes precedence over empty/populated states

**Empty State**:
- If `printers.length === 0` and `isLoading === false`, show empty state
- Empty state should be visually distinct but maintain design consistency

**Error State** (future consideration):
- Store could add `error: string | null` field for API errors
- Components could render error messages when error state is present
- For this phase, error handling is minimal (placeholder API returns empty array)

### Data Transformation

**Missing Fields**:
- If API response lacks required fields, transformation layer should provide defaults:
  - `status`: default to 'offline'
  - `toner_levels`: default to `{ cyan: 0, magenta: 0, yellow: 0, black: 0 }`
  - `capabilities`: default to `{ color: false, scanner: false }`

**Malformed Data**:
- Transformation layer should validate and sanitize data
- Invalid entries should be filtered out rather than causing crashes
- Log warnings for malformed data to aid debugging

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Test that ProvisioningPanel renders loading state when isLoading is true
- Test that ProvisioningPanel renders empty state when printers array is empty
- Test that API service placeholder returns empty array
- Test that transformation function handles missing fields with defaults
- Test component integration (store updates trigger re-renders)

**Property-Based Tests**: Verify universal properties across all inputs
- Test store operations with randomly generated printer data
- Test PrinterCard rendering with various printer configurations
- Test selection functionality with different printer collections
- Minimum 100 iterations per property test to ensure thorough coverage

### Property-Based Testing Configuration

**Library**: Use `fast-check` for TypeScript/JavaScript property-based testing

**Test Structure**:
Each property test should:
1. Generate random valid inputs using fast-check arbitraries
2. Execute the operation being tested
3. Assert the property holds
4. Run for minimum 100 iterations
5. Include a comment tag referencing the design property

**Example Tag Format**:
```typescript
// Feature: remove-static-data, Property 1: Store printer data round-trip
test('setPrinters and getPrinters maintain data integrity', () => {
  fc.assert(fc.property(
    fc.array(printerDeviceArbitrary),
    (printers) => {
      // Test implementation
    }
  ), { numRuns: 100 });
});
```

### Test Coverage Goals

**Store Tests**:
- Unit: Test initial state, individual method calls with specific examples
- Property: Test setPrinters/clearPrinters with random data, setLoading with random booleans

**Component Tests**:
- Unit: Test loading state rendering, empty state rendering, form presence, console presence
- Property: Test PrinterCard rendering with random printer data, selection with random IDs

**Integration Tests**:
- Unit: Test that calling API service updates store correctly
- Unit: Test that store updates trigger component re-renders

**Transformation Tests**:
- Unit: Test transformation with missing fields, malformed data
- Property: Test transformation preserves all fields for valid input

### Testing Tools

- **Test Runner**: Vitest (already configured in Vite projects)
- **Property Testing**: fast-check
- **Component Testing**: React Testing Library
- **Type Checking**: TypeScript compiler (tsc --noEmit)

### Test Execution

All tests should be runnable with:
```bash
npm run test        # Run all tests once
npm run test:watch  # Run tests in watch mode (manual use only)
```

Property tests should be configured to run 100+ iterations to catch edge cases through randomization.
