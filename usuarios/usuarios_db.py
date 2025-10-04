import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple


def fetch_roles_with_ids(db_path: str = "academia.db") -> List[Tuple[int, str]]:
    """Retorna lista de tuplas (rol_id, nombre_rol) ordenadas por rol_id."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT rol_id, nombre_rol FROM rol ORDER BY rol_id;")
            return [(int(rol_id), nombre_rol) for rol_id, nombre_rol in cur.fetchall()]
        finally:
            conn.close()
    except Exception:
        return []

        


def fetch_usuarios_for_table(db_path: str = "academia.db") -> List[Tuple[int, str, str]]:
    """Retorna lista de tuplas (usuario_id, nombre, nombre_rol) para la tabla."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.usuario_id, u.nombre, r.nombre_rol
                FROM usuario u
                LEFT JOIN usuario_rol ur ON u.usuario_id = ur.usuario_id
                LEFT JOIN rol r ON ur.rol_id = r.rol_id
                ORDER BY u.usuario_id;
            """)
            return [(int(usuario_id), nombre, nombre_rol or "Sin rol") for usuario_id, nombre, nombre_rol in cur.fetchall()]
        finally:
            conn.close()
    except Exception:
        return []


def fetch_usuario_by_id(usuario_id: int, db_path: str = "academia.db") -> Optional[Tuple[str, str, int]]:
    """Retorna (nombre, contrasena, rol_id) para el usuario dado."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.nombre, u.contrasena, ur.rol_id
                FROM usuario u
                LEFT JOIN usuario_rol ur ON u.usuario_id = ur.usuario_id
                WHERE u.usuario_id = ?;
            """, (usuario_id,))
            row = cur.fetchone()
            if row is None:
                return None
            nombre, contrasena, rol_id = row
            return (nombre, contrasena, rol_id or 0)
        finally:
            conn.close()
    except Exception:
        return None


def insert_usuario(nombre: str, contrasena: str, rol_id: int, db_path: str = "academia.db") -> Optional[int]:
    """Inserta un usuario y devuelve su nuevo usuario_id."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            # Insertar usuario
            cur.execute(
                """
                INSERT INTO usuario (nombre, contrasena)
                VALUES (?, ?);
                """,
                (nombre, contrasena)
            )
            usuario_id = int(cur.lastrowid)
            
            # Insertar relación usuario_rol si rol_id > 0
            if rol_id > 0:
                cur.execute(
                    """
                    INSERT INTO usuario_rol (usuario_id, rol_id)
                    VALUES (?, ?);
                    """,
                    (usuario_id, rol_id)
                )
            
            conn.commit()
            return usuario_id
        finally:
            conn.close()
    except Exception:
        return None


def update_usuario(usuario_id: int, nombre: str, contrasena: str, rol_id: int, db_path: str = "academia.db") -> bool:
    """Actualiza un usuario por su ID."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            # Actualizar usuario
            cur.execute(
                """
                UPDATE usuario
                SET nombre = ?, contrasena = ?
                WHERE usuario_id = ?;
                """,
                (nombre, contrasena, usuario_id)
            )
            
            # Actualizar rol
            cur.execute("DELETE FROM usuario_rol WHERE usuario_id = ?;", (usuario_id,))
            if rol_id > 0:
                cur.execute(
                    """
                    INSERT INTO usuario_rol (usuario_id, rol_id)
                    VALUES (?, ?);
                    """,
                    (usuario_id, rol_id)
                )
            
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def delete_usuario(usuario_id: int, db_path: str = "academia.db") -> bool:
    """Elimina un usuario por su ID."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            # Eliminar relaciones primero
            cur.execute("DELETE FROM usuario_rol WHERE usuario_id = ?;", (usuario_id,))
            # Eliminar usuario
            cur.execute("DELETE FROM usuario WHERE usuario_id = ?;", (usuario_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def is_user_admin(usuario_id: int, db_path: str = "academia.db") -> bool:
    """Verifica si un usuario tiene rol de administrador."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT r.nombre_rol
                FROM usuario_rol ur
                JOIN rol r ON ur.rol_id = r.rol_id
                WHERE ur.usuario_id = ? AND r.nombre_rol = 'administrador';
            """, (usuario_id,))
            result = cur.fetchone()
            return result is not None
        finally:
            conn.close()
    except Exception:
        return False