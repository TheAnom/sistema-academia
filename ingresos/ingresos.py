import tkinter as tk
from tkinter import ttk

try:
    from ingresos.ingresos_ui import IngresosView
except Exception as exc:
    # Fallback simple si UI aún no está lista
    class IngresosView(ttk.Frame):
        def __init__(self, parent: tk.Widget, usuario_id: int | None = None):
            super().__init__(parent)
            ttk.Label(self, text=f"UI Ingresos no disponible: {exc}").pack(padx=12, pady=12)


def create_ingresos_tab(parent: tk.Widget, usuario_id: int | None = None, on_logout_callback=None) -> tk.Widget:
    """Crea y devuelve el contenedor principal de la pestaña Ingresos.

    Este módulo actúa como orquestador: importa la vista y más adelante
    podrá inyectar servicios de datos definidos en ingresos_db.
    """
    return IngresosView(parent, usuario_id, on_logout_callback)


