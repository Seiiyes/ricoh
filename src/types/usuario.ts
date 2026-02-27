// Tipos para la gestión de usuarios

export interface ImpresoraUsuario {
  printer_id: number;
  printer_name: string;
  printer_ip: string;
  printer_location?: string;
  carpeta?: string;
  entry_index?: string;
  permisos?: {
    copiadora: boolean;
    copiadora_color?: boolean;
    impresora: boolean;
    impresora_color?: boolean;
    document_server: boolean;
    fax: boolean;
    escaner: boolean;
    navegador: boolean;
  };
}

export interface Usuario {
  id: number | string; // Puede ser número (DB) o string (impresora)
  name: string;
  codigo_de_usuario: string;
  empresa?: string;  // Empresa (antes email)
  centro_costos?: string;  // Centro de costos (antes department)

  // Credenciales de red
  network_username?: string;

  // Configuración SMB
  smb_server?: string;
  smb_port?: number;
  smb_path?: string;

  // Permisos disponibles
  func_copier: boolean;
  func_copier_color?: boolean;
  func_printer: boolean;
  func_printer_color?: boolean;
  func_document_server: boolean;
  func_fax: boolean;
  func_scanner: boolean;
  func_browser: boolean;

  // Metadatos
  is_active: boolean;
  created_at?: string;
  updated_at?: string;

  // Origen del usuario (para sincronización)
  origen?: 'db' | 'impresora';
  en_db?: boolean;

  // Impresoras donde está registrado el usuario
  impresoras?: ImpresoraUsuario[];

  // Campos legacy (para compatibilidad)
  printer_name?: string;
  printer_ip?: string;
}

export interface EquipoAsignado {
  id: number;
  hostname: string;
  ip_address: string;
  status: string;
}

export interface UsuarioConEquipos extends Usuario {
  equipos: EquipoAsignado[];
  total_equipos: number;
}

export interface ActualizarUsuario {
  name?: string;
  codigo_de_usuario?: string;
  empresa?: string;  // Empresa (antes email)
  centro_costos?: string;  // Centro de costos (antes department)
  network_username?: string;
  network_password?: string;
  smb_server?: string;
  smb_port?: number;
  smb_path?: string;
  func_copier?: boolean;
  func_copier_color?: boolean;
  func_printer?: boolean;
  func_printer_color?: boolean;
  func_document_server?: boolean;
  func_fax?: boolean;
  func_scanner?: boolean;
  func_browser?: boolean;
  is_active?: boolean;
}

export interface FiltrosUsuario {
  busqueda?: string;
  estado?: 'todos' | 'activos' | 'inactivos';
  equipoId?: number;
}
