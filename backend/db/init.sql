-- Initial database setup script
-- This runs automatically when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
DO $$ BEGIN
    CREATE TYPE printer_status AS ENUM ('online', 'offline', 'error', 'maintenance');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ricoh_fleet TO ricoh_admin;

-- Create indexes for performance (will be created by SQLAlchemy, but good to have as backup)
-- Additional custom indexes can be added here

-- Insert demo data (optional)
-- This will be handled by the application, but can be seeded here if needed
