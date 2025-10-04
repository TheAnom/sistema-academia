import tkinter as tk
from tkinter import ttk

try:
    from consultas.consultas_ui import ConsultasView
except Exception as exc:
    # Fallback simple si UI aún no está lista
    class ConsultasView(ttk.Frame):
        def __init__(self, parent: tk.Widget, on_logout_callback=None):
            super().__init__(parent)
            ttk.Label(self, text=f"UI Consultas no disponible: {exc}").pack(padx=12, pady=12)


def create_consultas_tab(parent: tk.Widget, on_logout_callback=None) -> tk.Widget:
    """Crea y devuelve el contenedor principal de la pestaña Consultas.

    Este módulo actúa como orquestador: importa la vista y más adelante
    podrá inyectar servicios de datos definidos en consultas_db.
    """
    return ConsultasView(parent, on_logout_callback)
