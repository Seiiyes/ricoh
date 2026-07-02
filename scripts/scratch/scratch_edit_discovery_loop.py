with open('backend/api/discovery.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_loop = -1
for i in range(len(lines)):
    if 'for printer in printers:' in lines[i] and 'Omitir' in lines[i+1]:
        start_loop = i
        break

end_loop = -1
for i in range(start_loop + 1, len(lines)):
    if 'close_selenium_client()' in lines[i]:
        end_loop = i
        break

if start_loop == -1 or end_loop == -1:
    print(f"Error: Loop index not found (start={start_loop}, end={end_loop})")
    import sys
    sys.exit(1)

print(f"Found loop start at line {start_loop + 1}, end at line {end_loop + 1}")

header = lines[:start_loop]

insert_code = """        import concurrent.futures
        
        active_printers = []
        for printer in printers:
            # Omitir impresoras Kyocera (.248 y .249) - no tienen usuarios registrados
            if printer.ip_address in ['192.168.91.248', '192.168.91.249']:
                printers_scanned.append({
                    'id': printer.id,
                    'hostname': printer.hostname,
                    'ip': printer.ip_address,
                    'users_count': 0,
                    'skipped': True,
                    'reason': 'Kyocera - sin usuarios'
                })
            else:
                active_printers.append(printer)
                
        # Ejecutar escaneo concurrente de red en un ThreadPoolExecutor
        results = []
        if active_printers:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(active_printers), 8)) as executor:
                futures = {
                    executor.submit(
                        scan_single_printer,
                        p.id,
                        p.hostname,
                        p.ip_address,
                        p.admin_password,
                        mode,
                        user_code,
                        ricoh_client
                    ): p for p in active_printers
                }
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())
                    
        # Procesar los resultados secuencialmente en el hilo principal
        for res in results:
            printer_id = res['printer_id']
            printer_hostname = res['printer_hostname']
            printer_ip = res['printer_ip']
            printer_users = res['users']
            error = res['error']
            
            if error:
                errors.append(f"Error en {printer_hostname} ({printer_ip}): {error}")
                printers_scanned.append({
                    'id': printer_id,
                    'hostname': printer_hostname,
                    'ip': printer_ip,
                    'users_count': 0,
                    'error': error
                })
                continue
                
            printers_scanned.append({
                'id': printer_id,
                'hostname': printer_hostname,
                'ip': printer_ip,
                'users_count': len(printer_users)
            })
            
            for user in printer_users:
                codigo = user['codigo']
                
                # Si buscamos usuario específico, verificar que coincida
                if mode == "specific" and codigo != user_code:
                    continue
                
                # Verificar si ya existe en DB (con caché para evitar queries repetidos)
                if codigo not in existing_users_cache:
                    existing = db.query(User).filter(
                        User.codigo_de_usuario == codigo
                    ).first()
                    existing_users_cache[codigo] = existing
                else:
                    existing = existing_users_cache[codigo]
                    
                # ACTUALIZACIÓN DE PERSISTENCIA:
                # Si ya existe en DB, actualizamos sus permisos reales para esta impresora
                if existing:
                    from db.repository import AssignmentRepository
                    AssignmentRepository.update_assignment_state(
                        db=db, 
                        user_id=existing.id, 
                        printer_id=printer_id, 
                        entry_index=user.get('entry_index', ''), 
                        permissions=user['permisos']
                    )

                # Si el usuario no existe en el diccionario, crearlo
                if codigo not in users_dict:
                    users_dict[codigo] = {
                        'nombre': user['nombre'],
                        'codigo': codigo,
                        'empresa': user.get('empresa', ''),
                        'permisos': user['permisos'],
                        'carpeta': user['carpeta'],
                        'en_db': existing is not None,
                        'impresoras': []  # Lista de impresoras donde está registrado
                    }
                
                # Agregar esta impresora a la lista del usuario con sus permisos específicos
                impresora_ya_existe = any(
                    imp['printer_id'] == printer_id 
                    for imp in users_dict[codigo]['impresoras']
                )
                
                if not impresora_ya_existe:
                    logger.debug(f"   ➕ Agregando {codigo} a impresora {printer_hostname} ({printer_ip})")
                    users_dict[codigo]['impresoras'].append({
                        'printer_id': printer_id,
                        'printer_name': printer_hostname,
                        'printer_ip': printer_ip,
                        'entry_index': user.get('entry_index'),
                        'permisos': user['permisos'],
                        'carpeta': user['carpeta']
                    })
                else:
                    logger.debug(f"   🔄 Actualizando {codigo} en impresora {printer_hostname} (ya existía)")
                    for imp in users_dict[codigo]['impresoras']:
                        if imp['printer_id'] == printer_id:
                            imp['entry_index'] = user.get('entry_index')
                            imp['permisos'] = user['permisos']
                            imp['carpeta'] = user['carpeta']
                            break
                
                # Actualizar campos globales si aún no están definidos
                if not any(users_dict[codigo]['permisos'].values()):
                     users_dict[codigo]['permisos'] = user['permisos']
                if not users_dict[codigo]['carpeta']:
                     users_dict[codigo]['carpeta'] = user['carpeta']
                     
        # Cerrar el cliente Selenium si se usó
        close_selenium_client()
"""

footer = lines[end_loop + 1:]

new_content = ''.join(header) + insert_code + ''.join(footer)

with open('backend/api/discovery.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Discovery loop updated successfully!")
