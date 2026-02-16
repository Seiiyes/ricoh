# Requirements Document: Ricoh User Provisioning

## Introduction

This document specifies the requirements for implementing complete Ricoh printer user provisioning functionality. The current system only captures basic user information (name, PIN, SMB path) and lacks critical fields required by Ricoh printers for full user configuration. This feature will extend the system to support all fields present in the Ricoh printer's web interface, including network credentials, available functions, and proper SMB folder configuration.

## Glossary

- **User**: A person who will be provisioned to use Ricoh printers
- **Código_de_usuario**: Numeric authentication code (e.g., "1014") that users enter at the printer to authenticate
- **Nº_de_registro**: Auto-incremental registration number assigned by the printer
- **Visualización_tecla**: Display name shown on the printer keypad, automatically copied from the user's full name
- **Autenticación_de_carpeta**: Network credentials (username and password) used for SMB folder access
- **Funciones_disponibles**: Set of printer capabilities enabled for a user (copier, printer, scanner, fax, etc.)
- **Carpeta_SMB**: Network folder configuration where scanned documents are saved
- **Sistema**: The Ricoh printer provisioning system
- **Backend**: Python FastAPI application managing user data and printer communication
- **Frontend**: React TypeScript application providing the user interface
- **Database**: PostgreSQL database storing user and printer information

## Requirements

### Requirement 1: User Data Model Extension

**User Story:** As a system administrator, I want the database to store all required Ricoh user fields, so that complete user configurations can be provisioned to printers.

#### Acceptance Criteria

1. THE Database SHALL store the user's full name (Nombre)
2. THE Database SHALL store the Código_de_usuario as a numeric string
3. THE Database SHALL store the network username (Nombre_de_usuario_de_inicio_de_sesión)
4. THE Database SHALL store the network password (Contraseña_de_inicio_de_sesión) in encrypted form
5. THE Database SHALL store the SMB server name
6. THE Database SHALL store the SMB port number
7. THE Database SHALL store the SMB folder path
8. THE Database SHALL store boolean flags for each available function (copier, printer, document_server, fax, scanner, browser)
9. THE Database SHALL store email address as an optional field
10. THE Database SHALL store department as an optional field
11. THE Database SHALL NOT store Nº_de_registro (managed by printer)
12. THE Database SHALL NOT store Visualización_tecla (derived from Nombre)

### Requirement 2: API Schema Validation

**User Story:** As a backend developer, I want Pydantic schemas to validate all user fields, so that invalid data is rejected before reaching the database.

#### Acceptance Criteria

1. WHEN a user creation request is received, THE Backend SHALL validate that Nombre is a non-empty string with maximum 100 characters
2. WHEN a user creation request is received, THE Backend SHALL validate that Código_de_usuario contains only numeric characters
3. WHEN a user creation request is received, THE Backend SHALL validate that Código_de_usuario has between 4 and 8 digits
4. WHEN network credentials are provided, THE Backend SHALL validate that the username is a non-empty string
5. WHEN network credentials are provided, THE Backend SHALL validate that the password is a non-empty string
6. WHEN SMB configuration is provided, THE Backend SHALL validate that server name is a non-empty string
7. WHEN SMB configuration is provided, THE Backend SHALL validate that port is a positive integer
8. WHEN SMB configuration is provided, THE Backend SHALL validate that path follows UNC format (starts with \\\\)
9. WHEN email is provided, THE Backend SHALL validate that it follows valid email format
10. WHEN available functions are provided, THE Backend SHALL validate that each is a boolean value

### Requirement 3: User Creation Endpoint Enhancement

**User Story:** As a frontend developer, I want the user creation API to accept all required fields, so that I can submit complete user configurations.

#### Acceptance Criteria

1. WHEN a POST request is made to /users, THE Backend SHALL accept all user fields in the request body
2. WHEN required fields are missing, THE Backend SHALL return a 400 error with descriptive validation messages
3. WHEN a user is successfully created, THE Backend SHALL return the complete user object including generated ID
4. WHEN a user is successfully created, THE Backend SHALL encrypt the network password before storage
5. WHEN a duplicate Código_de_usuario exists for the same printer, THE Backend SHALL return a 400 error
6. WHEN email is provided and already exists, THE Backend SHALL return a 400 error

### Requirement 4: Provisioning Service Enhancement

**User Story:** As a system administrator, I want the provisioning service to send complete user configurations to Ricoh printers, so that users have all required capabilities configured.

#### Acceptance Criteria

1. WHEN provisioning a user to a printer, THE Sistema SHALL send the user's full name (Nombre)
2. WHEN provisioning a user to a printer, THE Sistema SHALL send the Código_de_usuario
3. WHEN provisioning a user to a printer, THE Sistema SHALL send the network username for folder authentication
4. WHEN provisioning a user to a printer, THE Sistema SHALL send the network password for folder authentication
5. WHEN provisioning a user to a printer, THE Sistema SHALL send all enabled available functions
6. WHEN provisioning a user to a printer, THE Sistema SHALL send the complete SMB folder configuration (protocol, server, port, path)
7. WHEN provisioning a user to a printer, THE Sistema SHALL allow the printer to auto-generate Nº_de_registro
8. WHEN provisioning a user to a printer, THE Sistema SHALL allow the printer to auto-populate Visualización_tecla from Nombre
9. WHEN provisioning fails, THE Sistema SHALL return a descriptive error message
10. WHEN provisioning succeeds, THE Sistema SHALL log the successful configuration

### Requirement 5: Frontend Form Enhancement

**User Story:** As a system administrator, I want a comprehensive form to enter all user information, so that I can provision users with complete configurations.

#### Acceptance Criteria

1. THE Frontend SHALL display an input field labeled "Nombre Completo" for the user's full name
2. THE Frontend SHALL display an input field labeled "Código de usuario" for the authentication code
3. THE Frontend SHALL display an input field labeled "Nombre de usuario de inicio de sesión" for network username
4. THE Frontend SHALL display a password input field labeled "Contraseña de inicio de sesión" for network password
5. THE Frontend SHALL display checkboxes for Funciones_disponibles with Spanish labels (Copiadora, Impresora, Document Server, Fax, Escáner, Navegador)
6. THE Frontend SHALL display an input field labeled "Nombre de servidor" for SMB server
7. THE Frontend SHALL display an input field labeled "Puerto" for SMB port with default value 21
8. THE Frontend SHALL display an input field labeled "Ruta" for SMB folder path
9. THE Frontend SHALL display optional input fields for email and department
10. THE Frontend SHALL NOT display fields for Nº_de_registro or Visualización_tecla
11. WHEN the form is submitted with invalid data, THE Frontend SHALL display validation error messages
12. WHEN the form is submitted successfully, THE Frontend SHALL clear all input fields

### Requirement 6: Terminology Correction

**User Story:** As a user, I want consistent Spanish terminology throughout the application, so that the interface matches the Ricoh printer's terminology.

#### Acceptance Criteria

1. THE Sistema SHALL use "Código de usuario" instead of "PIN" in all user-facing text
2. THE Sistema SHALL use "Código de usuario" in database column names and API field names
3. THE Sistema SHALL use "Código de usuario" in frontend labels and placeholders
4. THE Sistema SHALL use "Autenticación de carpeta" for network credentials section
5. THE Sistema SHALL use "Funciones disponibles" for the capabilities section
6. THE Sistema SHALL use "Carpeta SMB" for the folder configuration section

### Requirement 7: Password Security

**User Story:** As a security administrator, I want network passwords to be encrypted, so that credentials are protected from unauthorized access.

#### Acceptance Criteria

1. WHEN a network password is received by the Backend, THE Sistema SHALL encrypt it before database storage
2. WHEN a user record is retrieved, THE Sistema SHALL NOT include the encrypted password in API responses
3. WHEN provisioning to a printer, THE Sistema SHALL decrypt the password only in memory
4. THE Sistema SHALL use industry-standard encryption (AES-256 or equivalent)
5. THE Sistema SHALL store encryption keys securely outside the codebase

### Requirement 8: Available Functions Configuration

**User Story:** As a system administrator, I want to enable or disable specific printer functions for each user, so that access can be controlled based on user roles.

#### Acceptance Criteria

1. WHEN creating a user, THE Frontend SHALL allow selection of any combination of available functions
2. WHEN no functions are selected, THE Backend SHALL reject the user creation with a validation error
3. WHEN at least one function is selected, THE Backend SHALL accept the user creation
4. WHEN provisioning to a printer, THE Sistema SHALL send only the enabled functions
5. THE Sistema SHALL support these functions: Copiadora, Impresora, Document Server, Fax, Escáner, Navegador

### Requirement 9: SMB Folder Configuration

**User Story:** As a system administrator, I want to configure complete SMB folder details for each user, so that scanned documents are saved to the correct network location.

#### Acceptance Criteria

1. WHEN configuring SMB settings, THE Frontend SHALL accept server name, port, and path as separate fields
2. WHEN SMB port is not provided, THE Sistema SHALL use default value 21
3. WHEN SMB path is provided, THE Backend SHALL validate it follows UNC format (\\\\server\\path)
4. WHEN provisioning to a printer, THE Sistema SHALL send protocol as "SMB"
5. WHEN provisioning to a printer, THE Sistema SHALL send all SMB configuration fields (server, port, path)

### Requirement 10: Data Migration

**User Story:** As a database administrator, I want existing user records to be migrated to the new schema, so that current users continue to work after the update.

#### Acceptance Criteria

1. WHEN the database schema is updated, THE Sistema SHALL preserve all existing user data
2. WHEN existing users lack new required fields, THE Sistema SHALL populate them with sensible defaults
3. WHEN existing users have "pin" field, THE Sistema SHALL migrate it to "codigo_de_usuario"
4. WHEN existing users have "smb_path" field, THE Sistema SHALL parse it into server and path components
5. WHEN migration fails for any user, THE Sistema SHALL log the error and continue with remaining users
6. WHEN migration completes, THE Sistema SHALL report the number of successfully migrated users
