import tkinter as tk
from tkinter import ttk

try:
    from usuarios.usuarios_ui import UsuariosView
except Exception as exc:
    # Fallback simple si UI aún no está lista
    class UsuariosView(ttk.Frame):
        def __init__(self, parent: tk.Widget, on_logout_callback=None):
            super().__init__(parent)
            ttk.Label(self, text=f"UI Usuarios no disponible: {exc}").pack(padx=12, pady=12)


def create_usuarios_tab(parent: tk.Widget, on_logout_callback=None) -> tk.Widget:
    """Crea y devuelve el contenedor principal de la pestaña Usuarios.

    Este módulo actúa como orquestador: importa la vista y más adelante
    podrá inyectar servicios de datos definidos en usuarios_db.
    """
    return UsuariosView(parent, on_logout_callback)
