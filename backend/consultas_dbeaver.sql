-- ============================================
-- CONSULTAS ÚTILES PARA DBEAVER
-- Base de datos: ricoh_fleet
-- ============================================

-- 1. Ver todos los usuarios
SELECT * FROM users ORDER BY created_at DESC;

-- 2. Ver todas las impresoras
SELECT * FROM printers ORDER BY created_at DESC;

-- 3. Ver asignaciones de usuarios a impresoras
SELECT 
    u.name as usuario,
    u.pin,
    p.hostname as impresora,
    p.ip_address,
    upa.provisioned_at as fecha_aprovisionamiento
FROM user_printer_assignments upa
JOIN users u ON upa.user_id = u.id
JOIN printers p ON upa.printer_id = p.id
ORDER BY upa.provisioned_at DESC;

-- 4. Contar impresoras por usuario
SELECT 
    u.name as usuario,
    COUNT(upa.printer_id) as total_impresoras
FROM users u
LEFT JOIN user_printer_assignments upa ON u.id = upa.user_id
GROUP BY u.id, u.name
ORDER BY total_impresoras DESC;

-- 5. Contar usuarios por impresora
SELECT 
    p.hostname as impresora,
    p.ip_address,
    COUNT(upa.user_id) as total_usuarios
FROM printers p
LEFT JOIN user_printer_assignments upa ON p.id = upa.printer_id
GROUP BY p.id, p.hostname, p.ip_address
ORDER BY total_usuarios DESC;

-- 6. Ver impresoras online
SELECT 
    hostname,
    ip_address,
    model,
    status,
    last_seen
FROM printers 
WHERE status = 'online'
ORDER BY hostname;

-- 7. Ver impresoras offline
SELECT 
    hostname,
    ip_address,
    model,
    status,
    last_seen
FROM printers 
WHERE status = 'offline'
ORDER BY last_seen DESC;

-- 8. Ver usuarios sin impresoras asignadas
SELECT 
    u.id,
    u.name,
    u.email,
    u.department
FROM users u
LEFT JOIN user_printer_assignments upa ON u.id = upa.user_id
WHERE upa.user_id IS NULL;

-- 9. Ver impresoras sin usuarios asignados
SELECT 
    p.id,
    p.hostname,
    p.ip_address,
    p.model
FROM printers p
LEFT JOIN user_printer_assignments upa ON p.id = upa.printer_id
WHERE upa.printer_id IS NULL;

-- 10. Estadísticas generales
SELECT 
    (SELECT COUNT(*) FROM users) as total_usuarios,
    (SELECT COUNT(*) FROM printers) as total_impresoras,
    (SELECT COUNT(*) FROM user_printer_assignments) as total_asignaciones,
    (SELECT COUNT(*) FROM printers WHERE status = 'online') as impresoras_online,
    (SELECT COUNT(*) FROM printers WHERE status = 'offline') as impresoras_offline;

-- 11. Ver capacidades de impresoras
SELECT 
    hostname,
    ip_address,
    (capabilities->>'color')::boolean as tiene_color,
    (capabilities->>'duplex')::boolean as tiene_duplex,
    (capabilities->>'scanner')::boolean as tiene_scanner,
    (capabilities->>'fax')::boolean as tiene_fax
FROM printers
ORDER BY hostname;

-- 12. Ver niveles de tóner
SELECT 
    hostname,
    ip_address,
    (toner_levels->>'cyan')::int as cyan,
    (toner_levels->>'magenta')::int as magenta,
    (toner_levels->>'yellow')::int as yellow,
    (toner_levels->>'black')::int as black
FROM printers
WHERE toner_levels IS NOT NULL
ORDER BY hostname;

-- 13. Últimas asignaciones (últimas 10)
SELECT 
    u.name as usuario,
    p.hostname as impresora,
    p.ip_address,
    upa.provisioned_at,
    AGE(NOW(), upa.provisioned_at) as hace
FROM user_printer_assignments upa
JOIN users u ON upa.user_id = u.id
JOIN printers p ON upa.printer_id = p.id
ORDER BY upa.provisioned_at DESC
LIMIT 10;

-- 14. Buscar usuario por nombre
SELECT * FROM users 
WHERE name ILIKE '%nombre%'
ORDER BY name;

-- 15. Buscar impresora por IP o hostname
SELECT * FROM printers 
WHERE ip_address ILIKE '%192.168%' 
   OR hostname ILIKE '%ricoh%'
ORDER BY hostname;
