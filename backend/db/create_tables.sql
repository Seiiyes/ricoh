-- Ricoh Fleet Governance - Database Schema
-- Execute this script to create all tables

-- Drop existing tables if they exist (careful in production!)
DROP TABLE IF EXISTS user_printer_assignments CASCADE;
DROP TABLE IF EXISTS printers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS printer_status CASCADE;

-- Create enum type for printer status
CREATE TYPE printer_status AS ENUM ('online', 'offline', 'error', 'maintenance');

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pin VARCHAR(255) NOT NULL,
    smb_path VARCHAR(500),
    email VARCHAR(255) UNIQUE,
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create printers table
CREATE TABLE printers (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    location VARCHAR(255),
    status printer_status DEFAULT 'offline',
    detected_model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    has_color BOOLEAN DEFAULT FALSE,
    has_scanner BOOLEAN DEFAULT FALSE,
    has_fax BOOLEAN DEFAULT FALSE,
    toner_cyan INTEGER DEFAULT 0 CHECK (toner_cyan >= 0 AND toner_cyan <= 100),
    toner_magenta INTEGER DEFAULT 0 CHECK (toner_magenta >= 0 AND toner_magenta <= 100),
    toner_yellow INTEGER DEFAULT 0 CHECK (toner_yellow >= 0 AND toner_yellow <= 100),
    toner_black INTEGER DEFAULT 0 CHECK (toner_black >= 0 AND toner_black <= 100),
    last_seen TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create user_printer_assignments table (many-to-many relationship)
CREATE TABLE user_printer_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    provisioned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    UNIQUE(user_id, printer_id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_printers_ip ON printers(ip_address);
CREATE INDEX idx_printers_hostname ON printers(hostname);
CREATE INDEX idx_printers_status ON printers(status);
CREATE INDEX idx_assignments_user ON user_printer_assignments(user_id);
CREATE INDEX idx_assignments_printer ON user_printer_assignments(printer_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_printers_updated_at BEFORE UPDATE ON printers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert demo data (optional)
INSERT INTO users (name, pin, smb_path, email, department) VALUES
('Juan Lizarazo', '1234', '\\10.0.0.5\scans\juan', 'juan.lizarazo@company.com', 'IT'),
('Maria Garcia', '5678', '\\10.0.0.5\scans\maria', 'maria.garcia@company.com', 'Finance'),
('Carlos Rodriguez', '9012', '\\10.0.0.5\scans\carlos', 'carlos.rodriguez@company.com', 'HR');

INSERT INTO printers (hostname, ip_address, location, status, detected_model, has_color, has_scanner, toner_cyan, toner_magenta, toner_yellow, toner_black) VALUES
('RICOH-MP-C3004-001', '192.168.1.100', 'Main Office - Floor 1', 'online', 'RICOH MP C3004', true, true, 75, 60, 85, 90),
('RICOH-SP-4510DN-001', '192.168.1.101', 'Main Office - Floor 2', 'online', 'RICOH SP 4510DN', false, false, 0, 0, 0, 45),
('RICOH-IM-C2500-001', '192.168.1.102', 'Conference Room A', 'online', 'RICOH IM C2500', true, true, 90, 85, 80, 95);

-- Verify tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Show table counts
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM printers) as total_printers,
    (SELECT COUNT(*) FROM user_printer_assignments) as total_assignments;
