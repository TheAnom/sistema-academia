from typing import List, Optional, Tuple
import sqlite3
from pathlib import Path


def fetch_estudiantes_for_autocomplete(db_path: str = "academia.db") -> List[Tuple[int, str]]:
    """Retorna lista de (estudiante_id, nombre_completo) para autocompletado."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT estudiante_id,
                       TRIM(COALESCE(nombre, '')) || ' ' || TRIM(COALESCE(apellido, '')) AS nombre_completo
                FROM estudiante
                WHERE TRIM(COALESCE(nombre, '')) || ' ' || TRIM(COALESCE(apellido, '')) != ' '
                ORDER BY nombre_completo ASC;
                """
            )
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def fetch_estudiante_complete_data(estudiante_id: int, db_path: str = "academia.db") -> Optional[Tuple[str, str, str, str]]:
    """Retorna (nombre_completo, grado, telefono, institucion) para el estudiante dado."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT TRIM(COALESCE(e.nombre, '')) || ' ' || TRIM(COALESCE(e.apellido, '')) AS nombre_completo,
                       COALESCE(g.nombre, '') AS grado,
                       COALESCE(e.telefono, '') AS telefono,
                       COALESCE(e.institucion, '') AS institucion
                FROM estudiante e
                LEFT JOIN grado g ON g.grado_id = e.grado_id
                WHERE e.estudiante_id = ?;
                """,
                (estudiante_id,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            return row
        finally:
            conn.close()
    except Exception:
        return None


def search_estudiantes_by_name(search_text: str, db_path: str = "academia.db") -> List[Tuple[int, str]]:
    """Busca estudiantes por nombre/apellido que contengan el texto de búsqueda."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            search_pattern = f"%{search_text.strip()}%"
            cur.execute(
                """
                SELECT estudiante_id,
                       TRIM(COALESCE(nombre, '')) || ' ' || TRIM(COALESCE(apellido, '')) AS nombre_completo
                FROM estudiante
                WHERE TRIM(COALESCE(nombre, '')) || ' ' || TRIM(COALESCE(apellido, '')) LIKE ?
                ORDER BY nombre_completo ASC;
                """,
                (search_pattern,)
            )
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def fetch_conceptos_pago_for_solvency(db_path: str = "academia.db") -> List[Tuple[int, str]]:
    """Retorna lista de (concepto_pago_id, nombre) para la tabla de solvencia."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT concepto_pago_id, nombre
                FROM concepto_pago
                ORDER BY concepto_pago_id ASC;
                """
            )
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def fetch_pagos_by_estudiante_and_concepto(estudiante_id: int, concepto_pago_id: int, db_path: str = "academia.db") -> List[float]:
    """Retorna lista de montos pagados por un estudiante para un concepto específico."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT monto
                FROM pago
                WHERE estudiante_id = ? AND concepto_pago_id = ?
                ORDER BY fecha DESC;
                """,
                (estudiante_id, concepto_pago_id)
            )
            return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()
    except Exception:
        return []


def check_solvency_status(estudiante_id: int, db_path: str = "academia.db") -> Tuple[bool, str]:
    """Verifica el estado de solvencia del estudiante basado en el mes actual."""
    from datetime import datetime
    
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Mapeo de meses a conceptos (asumiendo que los conceptos están ordenados por mes)
        month_concept_map = {
            1: 1,   # Enero
            2: 2,   # Febrero
            3: 3,   # Marzo
            4: 4,   # Abril
            5: 5,   # Mayo
            6: 6,   # Junio
            7: 7,   # Julio
            8: 8,   # Agosto
            9: 9,   # Septiembre
            10: 10, # Octubre
            11: 11, # Noviembre
            12: 12  # Diciembre
        }
        
        if current_month not in month_concept_map:
            return False, "No Solvente"
        
        concepto_id = month_concept_map[current_month]
        pagos = fetch_pagos_by_estudiante_and_concepto(estudiante_id, concepto_id, db_path)
        
        # Si hay pagos para el mes actual, está solvente
        if pagos:
            return True, "Solvente"
        else:
            return False, "No Solvente"
            
    except Exception:
        return False, "No Solvente"


def fetch_exam_conceptos_pago(db_path: str = "academia.db") -> List[Tuple[int, str]]:
    """Retorna lista de conceptos de pago para exámenes (asumiendo conceptos 13-17)."""
    try:
        if not Path(db_path).exists():
            return []
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT concepto_pago_id, nombre
                FROM concepto_pago
                WHERE concepto_pago_id >= 13 AND concepto_pago_id <= 17
                ORDER BY concepto_pago_id ASC;
                """
            )
            return cur.fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def fetch_calificaciones_by_estudiante(estudiante_id: int, db_path: str = "academia.db") -> Optional[Tuple[float, float, float, float]]:
    """Retorna las calificaciones del estudiante: (nota_uno, nota_dos, nota_tres, nota_cuatro)."""
    try:
        if not Path(db_path).exists():
            return None
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nota_uno, nota_dos, nota_tres, nota_cuatro
                FROM calificacion
                WHERE estudiante_id = ?
                ORDER BY calificacion_id DESC
                LIMIT 1;
                """,
                (estudiante_id,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            return (float(row[0] or 0), float(row[1] or 0), float(row[2] or 0), float(row[3] or 0))
        finally:
            conn.close()
    except Exception:
        return None


def calculate_average(notas: Tuple[float, float, float, float]) -> float:
    """Calcula el promedio de las 4 notas."""
    return sum(notas) / 4.0 if notas else 0.0


def is_approved(nota: float) -> bool:
    """Verifica si una nota está aprobada (mayor a 61)."""
    return nota > 61.0
