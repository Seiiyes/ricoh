-- Migration: Add user provisioning fields
-- Description: Adds all required fields for complete Ricoh user provisioning
-- Date: 2026-02-13

-- Step 1: Rename pin column to codigo_de_usuario
ALTER TABLE users RENAME COLUMN pin TO codigo_de_usuario;

-- Step 2: Add network credentials columns
ALTER TABLE users ADD COLUMN network_username VARCHAR(255) NOT NULL DEFAULT 'relitelda\scaner';
ALTER TABLE users ADD COLUMN network_password_encrypted TEXT NOT NULL DEFAULT '';

-- Step 3: Add SMB configuration columns
ALTER TABLE users ADD COLUMN smb_server VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE users ADD COLUMN smb_port INTEGER NOT NULL DEFAULT 21;

-- Note: smb_path column already exists, we'll keep it

-- Step 4: Add available functions columns
ALTER TABLE users ADD COLUMN func_copier BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN func_printer BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN func_document_server BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN func_fax BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN func_scanner BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN func_browser BOOLEAN NOT NULL DEFAULT FALSE;

-- Step 5: Migrate existing data
-- Parse smb_path to extract server name
UPDATE users 
SET smb_server = SPLIT_PART(REPLACE(smb_path, '\\', '/'), '/', 3)
WHERE smb_path IS NOT NULL AND smb_path LIKE '\\\\%';

-- Enable scanner function by default for all existing users
UPDATE users SET func_scanner = TRUE;

-- Step 6: Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_codigo_de_usuario ON users(codigo_de_usuario);

-- Migration complete
