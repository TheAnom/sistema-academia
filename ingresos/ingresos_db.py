from dataclasses import dataclass
from typing import List, Optional
import sqlite3
from pathlib import Path
from datetime import date


@dataclass
class Ingreso:
    id: int
    fecha: str
    concepto: str
    monto: float


class IngresosRepository:
    """Repositorio de datos para Ingresos.

    Por ahora es un stub en memoria. Luego se cambiará a SQLite u otro motor.
    """

    def __init__(self):
        self._items: List[Ingreso] = []
        self._next_id: int = 1

    def listar(self) -> List[Ingreso]:
        return list(self._items)

    def buscar(self, texto: str) -> List[Ingreso]:
        criterio = texto.lower().strip()
        return [i for i in self._items if criterio in i.concepto.lower()]

    def agregar(self, fecha: str, concepto: str, monto: float) -> Ingreso:
        item = Ingreso(id=self._next_id, fecha=fecha, concepto=concepto, monto=monto)
        self._items.append(item)
        self._next_id += 1
        return item

    def eliminar(self, ingreso_id: int) -> bool:
        for idx, item in enumerate(self._items):
            if item.id == ingreso_id:
                del self._items[idx]
                return True
        return False

    def obtener(self, ingreso_id: int) -> Optional[Ingreso]:
        for item in self._items:
            if item.id == ingreso_id:
                return item
        return None


def fetch_grados(db_path: str = "academia.db") -> List[str]:
    """Obtiene la lista de grados (campo nombre) desde la base de datos.

    Si la base o la tabla/campo no existen, devuelve una lista vacía.
    """
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT nombre FROM grado ORDER BY nombre ASC;")
            rows = cur.fetchall()
            return [r[0] for r in rows if r and r[0] is not None]
        finally:
            conn.close()
    except Exception:
        # Silencioso por ahora; en futuro se agregará logging
        return []


def fetch_grados_with_ids(db_path: str = "academia.db") -> List[tuple[int, str]]:
    """Retorna lista de tuplas (id, nombre) de la tabla grado."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT grado_id, nombre FROM grado ORDER BY nombre ASC;")
            rows = cur.fetchall()
            # Asegura tipos correctos
            result: List[tuple[int, str]] = []
            for r in rows:
                if r and r[0] is not None and r[1] is not None:
                    result.append((int(r[0]), str(r[1])))
            return result
        finally:
            conn.close()
    except Exception:
        return []


def fetch_conceptos_pago_with_ids(db_path: str = "academia.db") -> List[tuple[int, str]]:
    """Retorna lista de tuplas (id, nombre) de la tabla concepto_pago."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT concepto_pago_id, nombre FROM concepto_pago ORDER BY nombre ASC;")
            rows = cur.fetchall()
            result: List[tuple[int, str]] = []
            for r in rows:
                if r and r[0] is not None and r[1] is not None:
                    result.append((int(r[0]), str(r[1])))
            return result
        finally:
            conn.close()
    except Exception:
        return []


def fetch_estudiantes_for_table(db_path: str = "academia.db") -> List[tuple[int, str, str, str, str]]:
    """Retorna filas para tabla de estudiantes: (estudiante_id, NombreCompleto, Institucion, GradoNombre, Telefono)."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT e.estudiante_id,
                       TRIM(COALESCE(e.nombre, '')) || ' ' || TRIM(COALESCE(e.apellido, '')) AS nombre_completo,
                       e.institucion,
                       g.nombre AS grado,
                       e.telefono
                FROM estudiante e
                LEFT JOIN grado g ON g.grado_id = e.grado_id
                ORDER BY e.estudiante_id ASC;
                """
            )
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def fetch_pagos_for_table(db_path: str = "academia.db") -> List[tuple[int, str, str, str, float, str]]:
    """Retorna filas para tabla de pagos: (pago_id, ConceptoNombre, EstudianteNombre, UsuarioNombre, Monto, Fecha)."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT p.pago_id,
                       cp.nombre AS concepto,
                       TRIM(COALESCE(e.nombre, '')) || ' ' || TRIM(COALESCE(e.apellido, '')) AS estudiante,
                       u.nombre AS usuario,
                       p.monto,
                       p.fecha
                FROM pago p
                LEFT JOIN concepto_pago cp ON cp.concepto_pago_id = p.concepto_pago_id
                LEFT JOIN estudiante e ON e.estudiante_id = p.estudiante_id
                LEFT JOIN usuario u ON u.usuario_id = p.usuario_id
                ORDER BY p.pago_id ASC;
                """
            )
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def fetch_pago_by_id(pago_id: int, db_path: str = "academia.db") -> Optional[tuple[int, int, float, str]]:
    """Retorna (concepto_pago_id, estudiante_id, monto, fecha) para un pago."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT concepto_pago_id, estudiante_id, monto, fecha
                FROM pago
                WHERE pago_id = ?;
                """,
                (pago_id,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            concepto_pago_id, estudiante_id, monto, fecha = row
            return (int(concepto_pago_id), int(estudiante_id), float(monto), str(fecha))
        finally:
            conn.close()
    except Exception:
        return None


def update_pago(pago_id: int, concepto_pago_id: int, estudiante_id: int, usuario_id: int, monto: float, db_path: str = "academia.db") -> bool:
    """Actualiza un pago (fecha permanece igual)."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE pago
                SET concepto_pago_id = ?, estudiante_id = ?, usuario_id = ?, monto = ?
                WHERE pago_id = ?;
                """,
                (concepto_pago_id, estudiante_id, usuario_id, float(monto), pago_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def fetch_estudiante_by_id(estudiante_id: int, db_path: str = "academia.db") -> Optional[tuple[str, str, str, int, str]]:
    """Retorna (nombre, apellido, institucion, grado_id, telefono) para el estudiante dado."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nombre, apellido, institucion, grado_id, telefono
                FROM estudiante
                WHERE estudiante_id = ?;
                """,
                (estudiante_id,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            nombre, apellido, institucion, grado_id, telefono = row
            return (str(nombre or ""), str(apellido or ""), str(institucion or ""), int(grado_id) if grado_id is not None else 0, str(telefono or ""))
        finally:
            conn.close()
    except Exception:
        return None


def insert_estudiante(nombre: str, apellido: str, telefono: str, grado_id: int, institucion: str, db_path: str = "academia.db") -> Optional[int]:
    """Inserta un estudiante y devuelve su nuevo estudiante_id."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO estudiante (nombre, apellido, telefono, grado_id, institucion)
                VALUES (?, ?, ?, ?, ?);
                """,
                (nombre, apellido, telefono, grado_id, institucion)
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()
    except Exception:
        return None


def update_estudiante(estudiante_id: int, nombre: str, apellido: str, telefono: str, grado_id: int, institucion: str, db_path: str = "academia.db") -> bool:
    """Actualiza un estudiante por su ID."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE estudiante
                SET nombre = ?, apellido = ?, telefono = ?, grado_id = ?, institucion = ?
                WHERE estudiante_id = ?;
                """,
                (nombre, apellido, telefono, grado_id, institucion, estudiante_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def validar_credenciales(usuario: str, contrasena: str, db_path: str = "academia.db") -> bool:
    """Devuelve True si existe un registro en usuario(nombre, contrasena) que coincide exactamente."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 1 FROM usuario
                WHERE nombre = ? AND contrasena = ?
                LIMIT 1;
                """,
                (usuario, contrasena)
            )
            return cur.fetchone() is not None
        finally:
            conn.close()
    except Exception:
        return False


def authenticate_user(usuario: str, contrasena: str, db_path: str = "academia.db") -> Optional[int]:
    """Retorna usuario_id si las credenciales son válidas; None en caso contrario."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT usuario_id FROM usuario
                WHERE nombre = ? AND contrasena = ?
                LIMIT 1;
                """,
                (usuario, contrasena)
            )
            row = cur.fetchone()
            if row is None:
                return None
            return int(row[0])
        finally:
            conn.close()
    except Exception:
        return None


def insert_pago(concepto_pago_id: int, estudiante_id: int, usuario_id: int, monto: float, db_path: str = "academia.db") -> Optional[int]:
    """Inserta un pago con fecha actual (YYYY-MM-DD). Devuelve pago_id."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            fecha_hoy = date.today().isoformat()
            cur.execute(
                """
                INSERT INTO pago (concepto_pago_id, estudiante_id, usuario_id, monto, fecha)
                VALUES (?, ?, ?, ?, ?);
                """,
                (concepto_pago_id, estudiante_id, usuario_id, float(monto), fecha_hoy)
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()
    except Exception:
        return None


def insert_calificacion(estudiante_id: int, nota_uno: float, nota_dos: float, nota_tres: float, nota_cuatro: float, db_path: str = "academia.db") -> Optional[int]:
    """Inserta una calificación y devuelve su calificacion_id."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO calificacion (estudiante_id, nota_uno, nota_dos, nota_tres, nota_cuatro)
                VALUES (?, ?, ?, ?, ?);
                """,
                (estudiante_id, float(nota_uno), float(nota_dos), float(nota_tres), float(nota_cuatro))
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()
    except Exception:
        return None


def update_calificacion(calificacion_id: int, nota_uno: float, nota_dos: float, nota_tres: float, nota_cuatro: float, db_path: str = "academia.db") -> bool:
    """Actualiza una calificación por su ID."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE calificacion
                SET nota_uno = ?, nota_dos = ?, nota_tres = ?, nota_cuatro = ?
                WHERE calificacion_id = ?;
                """,
                (float(nota_uno), float(nota_dos), float(nota_tres), float(nota_cuatro), calificacion_id)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def fetch_calificacion_by_estudiante(estudiante_id: int, db_path: str = "academia.db") -> Optional[tuple[int, float, float, float, float]]:
    """Retorna (calificacion_id, nota_uno, nota_dos, nota_tres, nota_cuatro) para un estudiante."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT calificacion_id, nota_uno, nota_dos, nota_tres, nota_cuatro
                FROM calificacion
                WHERE estudiante_id = ?;
                """,
                (estudiante_id,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            calificacion_id, nota_uno, nota_dos, nota_tres, nota_cuatro = row
            return (int(calificacion_id), float(nota_uno), float(nota_dos), float(nota_tres), float(nota_cuatro))
        finally:
            conn.close()
    except Exception:
        return None


def delete_calificacion(calificacion_id: int, db_path: str = "academia.db") -> bool:
    """Elimina una calificación por su ID."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM calificacion
                WHERE calificacion_id = ?;
                """,
                (calificacion_id,)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def delete_pago(pago_id: int, db_path: str = "academia.db") -> bool:
    """Elimina un pago por su ID."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM pago
                WHERE pago_id = ?;
                """,
                (pago_id,)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False


def delete_estudiante_cascade(estudiante_id: int, db_path: str = "academia.db") -> bool:
    """Elimina un estudiante y todas sus relaciones (pagos, calificaciones)."""
    try:
        if not Path(db_path).exists():
            return False
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            # Eliminar en cascada: primero pagos, luego calificaciones, finalmente estudiante
            cur.execute("DELETE FROM pago WHERE estudiante_id = ?;", (estudiante_id,))
            cur.execute("DELETE FROM calificacion WHERE estudiante_id = ?;", (estudiante_id,))
            cur.execute("DELETE FROM estudiante WHERE estudiante_id = ?;", (estudiante_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()
    except Exception:
        return False





