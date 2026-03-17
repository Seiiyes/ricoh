# Requirements Document

## Introduction

This document defines the requirements for implementing automatic retry provisioning during user creation. Currently, users must be created in the database first, then manually provisioned to printers through the "Administrar Usuario" interface. When provisioning fails due to "device is being used" errors, users must retry manually. This feature will enable automatic provisioning during user creation with intelligent retry logic to handle temporary device busy states.

## Glossary

- **User_Creation_API**: The FastAPI endpoint that creates users in the database (`backend/api/users.py`)
- **Provisioning_Service**: The service that provisions users to Ricoh printers (`backend/services/provisioning.py`)
- **Ricoh_Web_Client**: The HTTP client that communicates with Ricoh printer web interfaces (`backend/services/ricoh_web_client.py`)
- **Device_Busy_Error**: The "BUSY" error returned by Ricoh printers when the device is being used by other operations
- **BADFLOW_Error**: Anti-scraping protection error returned by Ricoh printers when session flow is invalid
- **Printer_Assignment**: The database record linking a user to a printer with provisioning status
- **Retry_Strategy**: The algorithm that determines when and how many times to retry failed operations
- **Exponential_Backoff**: A retry strategy where wait time increases exponentially between attempts
- **Provisioning_Status**: The state of a provisioning operation (pending, in_progress, success, failed)

## Requirements

### Requirement 1: Accept Printer Selection During User Creation

**User Story:** As a system administrator, I want to select printers during user creation, so that I can provision users in one step instead of two separate operations.

#### Acceptance Criteria

1. THE User_Creation_API SHALL accept an optional list of printer IDs in the request payload
2. WHEN no printer IDs are provided, THE User_Creation_API SHALL create the user without provisioning (backward compatibility)
3. WHEN printer IDs are provided, THE User_Creation_API SHALL validate that all printer IDs exist in the database
4. IF any printer ID does not exist, THEN THE User_Creation_API SHALL return a 400 error with details of invalid printer IDs
5. THE User_Creation_API SHALL create the user in the database before attempting provisioning
6. IF user creation fails, THEN THE User_Creation_API SHALL not attempt provisioning

### Requirement 2: Automatic Provisioning After User Creation

**User Story:** As a system administrator, I want users to be automatically provisioned to selected printers after creation, so that I don't need to use "Administrar Usuario" for initial setup.

#### Acceptance Criteria

1. WHEN a user is created with printer IDs, THE User_Creation_API SHALL invoke the Provisioning_Service for each selected printer
2. THE Provisioning_Service SHALL provision the user to each printer sequentially (not in parallel)
3. FOR EACH printer, THE Provisioning_Service SHALL send the complete user configuration including network credentials, SMB settings, and available functions
4. THE Provisioning_Service SHALL record the provisioning status for each printer in the database
5. WHEN all provisioning attempts complete, THE User_Creation_API SHALL return the user data with provisioning results

### Requirement 3: Intelligent Retry for Device Busy Errors

**User Story:** As a system administrator, I want the system to automatically retry when printers are busy, so that provisioning succeeds without manual intervention.

#### Acceptance Criteria

1. WHEN the Ricoh_Web_Client receives a Device_Busy_Error, THE Provisioning_Service SHALL retry the provisioning operation
2. THE Provisioning_Service SHALL use exponential backoff with configurable parameters (initial delay, maximum delay, maximum attempts)
3. THE Provisioning_Service SHALL wait between 5 and 60 seconds between retry attempts, increasing exponentially
4. THE Provisioning_Service SHALL attempt provisioning at least 5 times before marking it as failed
5. WHEN a retry succeeds, THE Provisioning_Service SHALL stop retrying and mark the provisioning as successful
6. WHEN all retries are exhausted, THE Provisioning_Service SHALL mark the provisioning as failed and record the error
7. THE Provisioning_Service SHALL log each retry attempt with timestamp and attempt number

### Requirement 4: Handle BADFLOW and Other Errors

**User Story:** As a system administrator, I want the system to distinguish between temporary and permanent errors, so that it doesn't waste time retrying unrecoverable failures.

#### Acceptance Criteria

1. WHEN the Ricoh_Web_Client receives a BADFLOW_Error, THE Provisioning_Service SHALL reset the session and retry once
2. IF the BADFLOW_Error persists after session reset, THEN THE Provisioning_Service SHALL mark the provisioning as failed without further retries
3. WHEN the Ricoh_Web_Client receives a connection timeout, THE Provisioning_Service SHALL retry using the same strategy as Device_Busy_Error
4. WHEN the Ricoh_Web_Client receives a connection error, THE Provisioning_Service SHALL retry up to 3 times with 10 second delays
5. WHEN the Ricoh_Web_Client receives any other error, THE Provisioning_Service SHALL mark the provisioning as failed without retrying
6. THE Provisioning_Service SHALL record the specific error type and message for each failure

### Requirement 5: Partial Failure Handling

**User Story:** As a system administrator, I want to know which printers succeeded and which failed, so that I can take corrective action only where needed.

#### Acceptance Criteria

1. WHEN provisioning to multiple printers, THE User_Creation_API SHALL continue attempting all printers even if some fail
2. THE User_Creation_API SHALL return a response indicating overall success if at least one printer was provisioned successfully
3. THE User_Creation_API SHALL include a list of successfully provisioned printers with their IDs and hostnames
4. THE User_Creation_API SHALL include a list of failed printers with their IDs, hostnames, and error messages
5. THE User_Creation_API SHALL include a summary count of successful and failed provisioning operations
6. WHEN all printers fail, THE User_Creation_API SHALL return a 201 status (user created) with provisioning failure details

### Requirement 6: Configurable Retry Parameters

**User Story:** As a system administrator, I want to configure retry behavior, so that I can optimize for my network and printer characteristics.

#### Acceptance Criteria

1. THE Provisioning_Service SHALL read retry configuration from environment variables or configuration file
2. THE Provisioning_Service SHALL support configuration of initial retry delay (default: 5 seconds)
3. THE Provisioning_Service SHALL support configuration of maximum retry delay (default: 60 seconds)
4. THE Provisioning_Service SHALL support configuration of maximum retry attempts (default: 5)
5. THE Provisioning_Service SHALL support configuration of exponential backoff multiplier (default: 2.0)
6. WHEN configuration values are invalid or missing, THE Provisioning_Service SHALL use default values
7. THE Provisioning_Service SHALL log the active retry configuration at startup

### Requirement 7: Provisioning Status Feedback

**User Story:** As a system administrator, I want clear feedback about provisioning status, so that I understand what happened during user creation.

#### Acceptance Criteria

1. THE User_Creation_API SHALL return a response object containing user data and provisioning results
2. THE provisioning results SHALL include a boolean indicating overall success
3. THE provisioning results SHALL include the total number of printers attempted
4. THE provisioning results SHALL include the number of successful provisioning operations
5. THE provisioning results SHALL include the number of failed provisioning operations
6. FOR EACH printer, THE provisioning results SHALL include printer ID, hostname, IP address, status, and error message (if failed)
7. THE provisioning results SHALL include a human-readable summary message in Spanish
8. THE User_Creation_API SHALL use HTTP 201 status for successful user creation regardless of provisioning outcome

### Requirement 8: Maintain Backward Compatibility

**User Story:** As a developer, I want existing user creation flows to continue working, so that I don't break current functionality.

#### Acceptance Criteria

1. WHEN the User_Creation_API receives a request without printer IDs, THE system SHALL create the user without attempting provisioning
2. THE User_Creation_API SHALL accept both nested and flat data structures as it currently does
3. THE User_Creation_API SHALL continue to validate codigo_de_usuario uniqueness before creation
4. THE User_Creation_API SHALL continue to encrypt network passwords before storing
5. THE User_Creation_API SHALL return the same response structure for requests without printer IDs
6. THE existing "Administrar Usuario" provisioning interface SHALL continue to function unchanged

### Requirement 9: Logging and Observability

**User Story:** As a system administrator, I want detailed logs of provisioning operations, so that I can troubleshoot issues and monitor system behavior.

#### Acceptance Criteria

1. THE Provisioning_Service SHALL log the start of each provisioning operation with user name, code, and printer IP
2. THE Provisioning_Service SHALL log each retry attempt with attempt number, delay, and reason
3. THE Provisioning_Service SHALL log the final outcome (success or failure) for each printer
4. THE Provisioning_Service SHALL log the total time taken for each provisioning operation
5. THE Ricoh_Web_Client SHALL log all HTTP requests and responses at debug level
6. WHEN a Device_Busy_Error occurs, THE Provisioning_Service SHALL log the error with printer IP and timestamp
7. WHEN a BADFLOW_Error occurs, THE Provisioning_Service SHALL log the error and session reset action

### Requirement 10: Database Consistency

**User Story:** As a developer, I want database records to accurately reflect provisioning status, so that the system state is always consistent.

#### Acceptance Criteria

1. THE Provisioning_Service SHALL create a Printer_Assignment record only after successful provisioning to the physical printer
2. THE Provisioning_Service SHALL not create a Printer_Assignment record if provisioning fails after all retries
3. WHEN provisioning succeeds after retries, THE Printer_Assignment SHALL record the final successful timestamp
4. THE Printer_Assignment SHALL include the entry_index returned by the Ricoh printer
5. IF the user is deleted from the database, THE system SHALL not attempt to remove it from printers (existing behavior)
6. THE Provisioning_Service SHALL use database transactions to ensure atomicity of assignment creation
