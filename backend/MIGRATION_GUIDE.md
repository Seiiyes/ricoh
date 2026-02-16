# Database Migration Guide

This guide explains how to update your database to support the new user provisioning fields.

## Prerequisites

1. **Backup your database** before running any migration!
2. Install the new dependency:
   ```bash
   pip install cryptography==42.0.5
   ```
3. Set the encryption key in your `.env` file:
   ```bash
   # Generate a new key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Add to .env
   ENCRYPTION_KEY=your-generated-key-here
   ```

## Option 1: Migrate Existing Database (Recommended for Production)

Use this if you have existing users and want to preserve their data.

```bash
cd backend
python apply_migration.py
```

This will:
- Rename `pin` column to `codigo_de_usuario`
- Add network credentials fields (username, encrypted password)
- Add SMB configuration fields (server, port)
- Add available functions fields (6 boolean columns)
- Migrate existing data with sensible defaults
- Set a default password for all users (you'll need to update these)

**After migration:**
- All existing users will have the default password: `ChangeMe123!`
- Scanner function will be enabled by default
- You should update passwords through the admin interface

## Option 2: Recreate Database (Development Only)

⚠️ **WARNING: This deletes ALL data!**

Use this only for:
- Fresh installations
- Development environments
- When you don't need to preserve existing data

```bash
cd backend
python recreate_db.py
```

You'll need to type `DELETE ALL` to confirm.

## Option 3: Manual SQL Migration

If you prefer to run SQL manually:

```bash
cd backend
psql -U your_user -d your_database -f migrations/001_add_user_provisioning_fields.sql
```

## Verify Migration

After migration, verify the changes:

```bash
# Connect to your database
psql -U your_user -d your_database

# Check the users table structure
\d users

# You should see these new columns:
# - codigo_de_usuario (renamed from pin)
# - network_username
# - network_password_encrypted
# - smb_server
# - smb_port
# - func_copier
# - func_printer
# - func_document_server
# - func_fax
# - func_scanner
# - func_browser
```

## Rollback (if needed)

If something goes wrong, restore from your backup:

```bash
# Restore from backup
psql -U your_user -d your_database < backup.sql
```

## New Fields Reference

### Authentication
- `codigo_de_usuario` (VARCHAR): Numeric user code (4-8 digits)
- `network_username` (VARCHAR): Network login username (default: "relitelda\scaner")
- `network_password_encrypted` (TEXT): Encrypted network password

### SMB Configuration
- `smb_server` (VARCHAR): SMB server name or IP
- `smb_port` (INTEGER): SMB port (default: 21)
- `smb_path` (VARCHAR): Full UNC path (existing field)

### Available Functions
- `func_copier` (BOOLEAN): Copier function enabled
- `func_printer` (BOOLEAN): Printer function enabled
- `func_document_server` (BOOLEAN): Document server enabled
- `func_fax` (BOOLEAN): Fax function enabled
- `func_scanner` (BOOLEAN): Scanner function enabled
- `func_browser` (BOOLEAN): Browser function enabled

## Troubleshooting

### Error: "column already exists"
This is normal if you've run the migration before. The script will skip existing columns.

### Error: "relation does not exist"
Make sure your database is initialized. Run `python init_db.py` first.

### Error: "ENCRYPTION_KEY not set"
Add the encryption key to your `.env` file (see Prerequisites).

## Next Steps

After successful migration:

1. Update the backend API (already done)
2. Update the frontend to use new fields
3. Test user creation with new fields
4. Update existing user passwords
5. Configure available functions for each user
