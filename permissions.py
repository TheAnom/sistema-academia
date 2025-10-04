"""
Sistema de permisos para la aplicación Academia.

Define los permisos por rol y funciones para verificar acceso basado en la tabla permiso_rol.
"""

from typing import Dict, List, Set
import sqlite3
from pathlib import Path


# Mapeo de permisos a pestañas (basado en la funcionalidad)
PERMISSION_TO_TAB_MAPPING = {
    "Crear Usuarios": "registro_usuarios",
    "Eliminar Usuarios": "registro_usuarios", 
    "Modificar Usuarios": "registro_usuarios",
    "Consultar Usuarios": "registro_usuarios",
    "Registrar Estudiantes": "ingresos",
    "Eliminar Estudiantes": "ingresos",
    "Modificar Estudiantes": "ingresos",
    "Consultar Estudiantes": "consultas",
    "Registrar Notas": "ingresos",
    "Eliminar Notas": "ingresos",
    "Modificar Notas": "ingresos",
    "Consultar Notas": "consultas",
    "Registrar Pagos": "ingresos",
    "Consultar Pagos": "consultas",
    "Modificar Pagos": "ingresos",
    "Eliminar Pagos": "ingresos",
}


def get_user_role(usuario_id: int, db_path: str = "academia.db") -> str | None:
    """
    Obtiene el rol de un usuario por su ID.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        Nombre del rol o None si no se encuentra
    """
    try:
        if not Path(db_path).exists():
            return None
            
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.nombre_rol
                FROM usuario u
                JOIN usuario_rol ur ON u.usuario_id = ur.usuario_id
                JOIN rol r ON ur.rol_id = r.rol_id
                WHERE u.usuario_id = ?;
            """, (usuario_id,))
            
            result = cur.fetchone()
            return result[0] if result else None
            
        finally:
            conn.close()
    except Exception:
        return None


def has_tab_permission(usuario_id: int, tab_name: str, db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario tiene permiso para acceder a una pestaña.
    
    Args:
        usuario_id: ID del usuario
        tab_name: Nombre de la pestaña (ingresos, consultas, registro_usuarios)
        db_path: Ruta a la base de datos
        
    Returns:
        True si tiene permiso, False en caso contrario
    """
    try:
        if not Path(db_path).exists():
            return False
            
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            # Buscar si el usuario tiene algún permiso que mapee a la pestaña solicitada
            cur.execute("""
                SELECT COUNT(*) 
                FROM usuario u
                JOIN usuario_rol ur ON u.usuario_id = ur.usuario_id
                JOIN rol r ON ur.rol_id = r.rol_id
                JOIN permiso_rol pr ON r.rol_id = pr.rol_id
                JOIN permiso p ON pr.permiso_id = p.permiso_id
                WHERE u.usuario_id = ? AND ? IN (
                    SELECT DISTINCT tab_name 
                    FROM (
                        SELECT 'registro_usuarios' as tab_name WHERE p.nombre_permiso IN ('Crear Usuarios', 'Eliminar Usuarios', 'Modificar Usuarios', 'Consultar Usuarios')
                        UNION
                        SELECT 'ingresos' as tab_name WHERE p.nombre_permiso IN ('Registrar Estudiantes', 'Eliminar Estudiantes', 'Modificar Estudiantes', 'Registrar Notas', 'Eliminar Notas', 'Modificar Notas', 'Registrar Pagos', 'Modificar Pagos', 'Eliminar Pagos')
                        UNION
                        SELECT 'consultas' as tab_name WHERE p.nombre_permiso IN ('Consultar Estudiantes', 'Consultar Notas', 'Consultar Pagos')
                    )
                );
            """, (usuario_id, tab_name))
            
            result = cur.fetchone()
            return result[0] > 0 if result else False
            
        finally:
            conn.close()
    except Exception:
        return False


def has_action_permission(usuario_id: int, action: str, db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario tiene permiso para realizar una acción específica.
    
    Args:
        usuario_id: ID del usuario
        action: Acción a verificar (ej: "Crear Usuarios", "Consultar Estudiantes", etc.)
        db_path: Ruta a la base de datos
        
    Returns:
        True si tiene permiso, False en caso contrario
    """
    try:
        if not Path(db_path).exists():
            return False
            
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) 
                FROM usuario u
                JOIN usuario_rol ur ON u.usuario_id = ur.usuario_id
                JOIN rol r ON ur.rol_id = r.rol_id
                JOIN permiso_rol pr ON r.rol_id = pr.rol_id
                JOIN permiso p ON pr.permiso_id = p.permiso_id
                WHERE u.usuario_id = ? AND p.nombre_permiso = ?;
            """, (usuario_id, action))
            
            result = cur.fetchone()
            return result[0] > 0 if result else False
            
        finally:
            conn.close()
    except Exception:
        return False


def get_user_permissions(usuario_id: int, db_path: str = "academia.db") -> Dict[str, any]:
    """
    Obtiene todos los permisos de un usuario.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        Diccionario con los permisos del usuario
    """
    try:
        if not Path(db_path).exists():
            return {"tabs": [], "actions": []}
            
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.nombre_permiso
                FROM usuario u
                JOIN usuario_rol ur ON u.usuario_id = ur.usuario_id
                JOIN rol r ON ur.rol_id = r.rol_id
                JOIN permiso_rol pr ON r.rol_id = pr.rol_id
                JOIN permiso p ON pr.permiso_id = p.permiso_id
                WHERE u.usuario_id = ?
                ORDER BY p.nombre_permiso;
            """, (usuario_id,))
            
            permissions = [row[0] for row in cur.fetchall()]
            
            # Mapear permisos a pestañas
            tabs = set()
            for permission in permissions:
                if permission in PERMISSION_TO_TAB_MAPPING:
                    tabs.add(PERMISSION_TO_TAB_MAPPING[permission])
            
            return {
                "tabs": list(tabs),
                "actions": permissions
            }
            
        finally:
            conn.close()
    except Exception:
        return {"tabs": [], "actions": []}


def get_accessible_tabs(usuario_id: int, db_path: str = "academia.db") -> List[str]:
    """
    Obtiene la lista de pestañas accesibles para un usuario.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        Lista de nombres de pestañas accesibles
    """
    permissions = get_user_permissions(usuario_id, db_path)
    return permissions.get("tabs", [])


def is_admin(usuario_id: int, db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario es administrador.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        True si es administrador, False en caso contrario
    """
    return get_user_role(usuario_id, db_path) == "administrador"


def is_teacher(usuario_id: int, db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario es docente suplente.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        True si es docente suplente, False en caso contrario
    """
    return get_user_role(usuario_id, db_path) == "docente suplente"


def is_consultant(usuario_id: int, db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario es consultor.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        True si es consultor, False en caso contrario
    """
    return get_user_role(usuario_id, db_path) == "consultor"


def get_user_permissions_list(usuario_id: int, db_path: str = "academia.db") -> List[str]:
    """
    Obtiene la lista completa de permisos de un usuario.
    
    Args:
        usuario_id: ID del usuario
        db_path: Ruta a la base de datos
        
    Returns:
        Lista de nombres de permisos
    """
    permissions = get_user_permissions(usuario_id, db_path)
    return permissions.get("actions", [])


def has_any_permission(usuario_id: int, permissions: List[str], db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario tiene al menos uno de los permisos especificados.
    
    Args:
        usuario_id: ID del usuario
        permissions: Lista de permisos a verificar
        db_path: Ruta a la base de datos
        
    Returns:
        True si tiene al menos uno de los permisos, False en caso contrario
    """
    user_permissions = get_user_permissions_list(usuario_id, db_path)
    return any(perm in user_permissions for perm in permissions)


def has_all_permissions(usuario_id: int, permissions: List[str], db_path: str = "academia.db") -> bool:
    """
    Verifica si un usuario tiene todos los permisos especificados.
    
    Args:
        usuario_id: ID del usuario
        permissions: Lista de permisos a verificar
        db_path: Ruta a la base de datos
        
    Returns:
        True si tiene todos los permisos, False en caso contrario
    """
    user_permissions = get_user_permissions_list(usuario_id, db_path)
    return all(perm in user_permissions for perm in permissions)
