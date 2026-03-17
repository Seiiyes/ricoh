# Implementation Plan: Automatic Retry Provisioning

## Overview

This implementation plan breaks down the automatic retry provisioning feature into discrete coding tasks. The feature enables automatic provisioning of users to Ricoh printers during user creation with intelligent retry logic for handling transient errors (BUSY, TIMEOUT) and session errors (BADFLOW).

The implementation follows four phases:
1. Core retry logic infrastructure
2. Provisioning service enhancement with retry integration
3. API layer modifications for printer selection
4. Testing and validation

## Tasks

- [x] 1. Set up retry strategy infrastructure
  - [x] 1.1 Create RetryStrategy class with exponential backoff
    - Create `backend/services/retry_strategy.py`
    - Implement `RetryConfig` dataclass with configuration parameters
    - Implement `RetryStrategy` class with `should_retry()` method
    - Implement exponential backoff calculation: `initial_delay * (multiplier ^ (attempt - 1))`
    - Implement error-specific retry logic (BUSY, BADFLOW, TIMEOUT, CONNECTION, OTHER)
    - _Requirements: 3.2, 3.3, 3.4, 4.1, 4.2, 4.4, 4.5, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 1.2 Write property test for exponential backoff calculation
    - **Property 4: Exponential Backoff Calculation**
    - **Validates: Requirements 3.2, 3.3**
  
  - [ ]* 1.3 Write property test for retry attempt limits
    - **Property 5: Retry Attempt Limits**
    - **Validates: Requirements 3.4, 4.1, 4.2, 4.4, 4.5**
  
  - [x] 1.4 Implement configuration loading from environment variables
    - Implement `load_retry_config_from_env()` function
    - Read environment variables with fallback to defaults
    - Add validation for configuration values
    - _Requirements: 6.1, 6.6_
  
  - [ ]* 1.5 Write property test for configuration defaults
    - **Property 13: Configuration Defaults**
    - **Validates: Requirements 6.6**
  
  - [ ]* 1.6 Write unit tests for RetryStrategy
    - Test each error type's retry behavior
    - Test configuration loading with valid/invalid values
    - Test edge cases (attempt=0, negative delays)
    - _Requirements: 3.2, 3.3, 3.4, 4.1, 4.2, 4.4, 4.5_

- [x] 2. Enhance RicohWebClient error handling
  - [x] 2.1 Add timeout and connection error detection
    - Modify `provision_user()` in `backend/services/ricoh_web_client.py`
    - Add try-except for `requests.exceptions.Timeout` → return "TIMEOUT"
    - Add try-except for `requests.exceptions.ConnectionError` → return "CONNECTION"
    - Ensure existing BUSY and BADFLOW detection remains unchanged
    - _Requirements: 4.3, 4.4_
  
  - [ ]* 2.2 Write unit tests for error detection
    - Test timeout error returns "TIMEOUT"
    - Test connection error returns "CONNECTION"
    - Test BUSY error returns "BUSY"
    - Test BADFLOW error returns "BADFLOW"
    - _Requirements: 4.3, 4.4_

- [ ] 3. Checkpoint - Verify retry infrastructure
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement provisioning service retry logic
  - [x] 4.1 Create _provision_to_single_printer() method
    - Add method to `ProvisioningService` in `backend/services/provisioning.py`
    - Implement retry loop with attempt counter
    - Integrate `RetryStrategy.should_retry()` for retry decisions
    - Add BADFLOW session reset logic (reset on first attempt, fail on second)
    - Add logging for each attempt, retry, and final outcome
    - Calculate and log elapsed time
    - _Requirements: 3.1, 3.5, 3.6, 3.7, 4.1, 4.2, 4.6, 9.1, 9.2, 9.3, 9.4, 9.6, 9.7_
  
  - [x] 4.2 Implement _classify_provisioning_result() method
    - Map RicohWebClient return values to ErrorType
    - Return None for success (True)
    - Return appropriate ErrorType for each error string
    - _Requirements: 3.1, 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 4.3 Implement _format_error_message() method
    - Create Spanish error messages for each ErrorType
    - Return user-friendly descriptions
    - _Requirements: 4.6, 7.6_
  
  - [ ]* 4.4 Write property test for early termination on success
    - **Property 6: Early Termination on Success**
    - **Validates: Requirements 3.5**
  
  - [ ]* 4.5 Write property test for failure after exhausted retries
    - **Property 7: Failure After Exhausted Retries**
    - **Validates: Requirements 3.6, 4.6**
  
  - [ ]* 4.6 Write property test for BADFLOW session reset
    - **Property 8: BADFLOW Session Reset**
    - **Validates: Requirements 4.1, 4.2**
  
  - [ ]* 4.7 Write unit tests for single printer provisioning
    - Test successful provisioning on first attempt
    - Test successful provisioning after retries
    - Test failure after all retries exhausted
    - Test BADFLOW with session reset
    - _Requirements: 3.1, 3.5, 3.6, 4.1, 4.2_

- [x] 5. Enhance provision_user_to_printers() method
  - [x] 5.1 Modify provision_user_to_printers() to use retry logic
    - Modify method in `backend/services/provisioning.py`
    - Initialize `RetryStrategy` with loaded configuration
    - Loop through printers sequentially (not parallel)
    - Call `_provision_to_single_printer()` for each printer
    - Continue to next printer even if one fails
    - Create `UserPrinterAssignment` record only on success
    - Build results list with all printer outcomes
    - Calculate summary (overall_success, counts, message)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1, 5.2, 5.3, 5.4, 5.5, 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 5.2 Write property test for sequential provisioning order
    - **Property 2: Sequential Provisioning Order**
    - **Validates: Requirements 2.2**
  
  - [ ]* 5.3 Write property test for partial failure independence
    - **Property 9: Partial Failure Independence**
    - **Validates: Requirements 5.1**
  
  - [ ]* 5.4 Write property test for overall success criteria
    - **Property 10: Overall Success Criteria**
    - **Validates: Requirements 5.2**
  
  - [ ]* 5.5 Write property test for database-printer consistency
    - **Property 17: Database-Printer Consistency**
    - **Validates: Requirements 10.1, 10.2**
  
  - [ ]* 5.6 Write unit tests for multi-printer provisioning
    - Test all printers succeed
    - Test partial success (some succeed, some fail)
    - Test all printers fail
    - Test database assignment creation
    - _Requirements: 2.1, 2.2, 5.1, 5.2, 10.1, 10.2_

- [ ] 6. Checkpoint - Verify provisioning service
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Create API schemas for provisioning
  - [x] 7.1 Add printer_ids field to UserCreate schema
    - Modify `UserCreate` in `backend/api/schemas.py`
    - Add `printer_ids: Optional[List[int]]` field
    - Add validator to ensure all printer IDs are positive
    - _Requirements: 1.1, 1.2_
  
  - [x] 7.2 Create PrinterProvisioningResult schema
    - Add `PrinterProvisioningResult` class to `backend/api/schemas.py`
    - Include fields: printer_id, hostname, ip_address, status, error_message, retry_attempts, provisioned_at
    - _Requirements: 5.3, 5.4, 7.6_
  
  - [x] 7.3 Create ProvisioningResults schema
    - Add `ProvisioningResults` class to `backend/api/schemas.py`
    - Include fields: overall_success, total_printers, successful_count, failed_count, results, summary_message
    - _Requirements: 5.5, 7.2, 7.3, 7.4, 7.5, 7.7_
  
  - [x] 7.4 Create UserCreateResponse schema
    - Add `UserCreateResponse` class extending `UserResponse`
    - Add `provisioning_results: Optional[ProvisioningResults]` field
    - _Requirements: 7.1_
  
  - [ ]* 7.5 Write property test for complete response structure
    - **Property 11: Complete Response Structure**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7**

- [x] 8. Modify user creation API endpoint
  - [x] 8.1 Add printer ID validation to create_user()
    - Modify `create_user()` in `backend/api/users.py`
    - Validate all printer IDs exist in database before user creation
    - Return 400 error with details if any printer ID is invalid
    - _Requirements: 1.3, 1.4_
  
  - [x] 8.2 Integrate automatic provisioning after user creation
    - Call `ProvisioningService.provision_user_to_printers()` after user creation
    - Only call if `printer_ids` is provided and not empty
    - Wrap provisioning in try-except to prevent user creation rollback
    - Build error response if provisioning throws exception
    - _Requirements: 1.5, 1.6, 2.1, 2.5_
  
  - [x] 8.3 Update response to include provisioning results
    - Change response_model to `UserCreateResponse`
    - Include provisioning_results in response data
    - Ensure HTTP 201 status regardless of provisioning outcome
    - _Requirements: 7.1, 7.8_
  
  - [x] 8.4 Ensure backward compatibility
    - Verify requests without printer_ids work unchanged
    - Verify existing validation (codigo uniqueness) still works
    - Verify password encryption still works
    - _Requirements: 1.2, 8.1, 8.3, 8.4, 8.5_
  
  - [ ]* 8.5 Write property test for printer ID validation
    - **Property 1: Printer ID Validation**
    - **Validates: Requirements 1.3, 1.4**
  
  - [ ]* 8.6 Write property test for HTTP 201 on user creation success
    - **Property 12: HTTP 201 on User Creation Success**
    - **Validates: Requirements 7.8**
  
  - [ ]* 8.7 Write property test for backward compatibility
    - **Property 14: Backward Compatibility Without Printer IDs**
    - **Validates: Requirements 1.2, 8.1, 8.5**
  
  - [ ]* 8.8 Write integration tests for user creation with provisioning
    - Test user creation with valid printer IDs
    - Test user creation with invalid printer IDs
    - Test user creation without printer IDs (backward compatibility)
    - Test user creation with duplicate codigo_de_usuario
    - Mock RicohWebClient to return various error sequences
    - Verify database state after each scenario
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.5, 8.1, 8.3, 8.4, 8.5_

- [x] 9. Add configuration documentation
  - [x] 9.1 Update .env.example with retry configuration
    - Add all retry configuration environment variables
    - Include comments explaining each parameter
    - Document default values
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ] 10. Final checkpoint - End-to-end validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows with mocked dependencies
- The implementation maintains backward compatibility - existing user creation flows are unaffected
- No database schema changes are required
- Configuration uses sensible defaults - no environment variables required for basic operation
