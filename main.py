import tkinter as tk
from tkinter import ttk

# Importa Login
try:
    from login.login import create_login_frame
except Exception as exc:
    def create_login_frame(parent: tk.Widget, on_success):  # type: ignore
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=f"Error cargando Login: {exc}").pack(padx=12, pady=12)
        return frame

# Importa el módulo principal de la sección Ingresos
try:
    from ingresos.ingresos import create_ingresos_tab
except Exception as exc:
    # Fallback temporal si el módulo aún no existe
    def create_ingresos_tab(parent: tk.Widget) -> tk.Widget:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=f"Error cargando Ingresos: {exc}").pack(padx=12, pady=12)
        return frame

# Importa el módulo de gestión de usuarios
try:
    from usuarios.registro_usuarios import create_usuarios_tab
except Exception as exc:
    # Fallback temporal si el módulo aún no existe
    def create_usuarios_tab(parent: tk.Widget, on_logout_callback=None) -> tk.Widget:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=f"Error cargando Usuarios: {exc}").pack(padx=12, pady=12)
        return frame

# Importa el sistema de permisos
try:
    from permissions import (
        has_tab_permission, 
        get_accessible_tabs, 
        get_user_role,
        is_admin
    )
except Exception as exc:
    # Fallback temporal si el módulo aún no existe
    def has_tab_permission(usuario_id: int, tab_name: str, db_path: str = "academia.db") -> bool:
        return True  # Permitir todo por defecto
    def get_accessible_tabs(usuario_id: int, db_path: str = "academia.db") -> list:
        return ["ingresos", "consultas", "registro_usuarios"]
    def get_user_role(usuario_id: int, db_path: str = "academia.db") -> str:
        return "administrador"
    def is_admin(usuario_id: int, db_path: str = "academia.db") -> bool:
        return True

# Importa el módulo de consultas
try:
    from consultas.consultas import create_consultas_tab
except Exception as exc:
    # Fallback temporal si el módulo aún no existe
    def create_consultas_tab(parent: tk.Widget, on_logout_callback=None) -> tk.Widget:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=f"Error cargando Consultas: {exc}").pack(padx=12, pady=12)
        return frame


def create_main_window() -> tk.Tk:
    root = tk.Tk()
    root.title("Gestión de Pagos y Notas")
    
    # Configurar DPI awareness para Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Configurar colores del sistema con paleta educativa profesional
    style = ttk.Style()
    
    # Paleta de colores para institución educativa
    # Azul institucional (principal)
    PRIMARY_BLUE = "#1e3a8a"      # Azul profundo institucional
    LIGHT_BLUE = "#3b82f6"        # Azul claro para acentos
    SOFT_BLUE = "#dbeafe"         # Azul muy claro para fondos
    
    # Verde académico (secundario)
    ACADEMIC_GREEN = "#059669"    # Verde académico
    LIGHT_GREEN = "#10b981"       # Verde claro
    SOFT_GREEN = "#d1fae5"        # Verde muy claro
    
    # Grises profesionales
    DARK_GRAY = "#1f2937"         # Gris oscuro para fondos
    MEDIUM_GRAY = "#4b5563"       # Gris medio
    LIGHT_GRAY = "#f3f4f6"        # Gris claro para fondos
    WHITE = "#ffffff"             # Blanco puro
    
    # Colores de estado
    SUCCESS_GREEN = "#10b981"     # Verde éxito
    WARNING_ORANGE = "#f59e0b"    # Naranja advertencia
    ERROR_RED = "#ef4444"         # Rojo error
    INFO_BLUE = "#3b82f6"         # Azul información
    
    # Configurar tema base
    style.theme_use('clam')
    
    # Configurar pestañas con estilo educativo
    style.configure("TNotebook", background=SOFT_BLUE, borderwidth=0)
    style.configure("TNotebook.Tab", 
                   background=LIGHT_GRAY, 
                   foreground=DARK_GRAY,
                   font=("Segoe UI", 10, "bold"),
                   padding=[20, 10])
    style.map("TNotebook.Tab",
              background=[('selected', PRIMARY_BLUE),
                         ('active', LIGHT_BLUE)],
              foreground=[('selected', WHITE),
                         ('active', WHITE)])
    
    # Configurar frames principales
    style.configure("TFrame", background=SOFT_BLUE)
    style.configure("Card.TFrame", 
                   background=WHITE, 
                   relief="solid", 
                   borderwidth=2,
                   bordercolor=PRIMARY_BLUE)
    
    # Frame especial para el login con efecto de elevación
    style.configure("LoginCard.TFrame", 
                   background=WHITE, 
                   relief="raised", 
                   borderwidth=3,
                   bordercolor=LIGHT_BLUE)
    
    # Configurar labels con tipografía mejorada
    style.configure("TLabel", 
                   background=SOFT_BLUE, 
                   foreground=DARK_GRAY, 
                   font=("Segoe UI", 10))
    style.configure("Title.TLabel", 
                   background=SOFT_BLUE, 
                   foreground=PRIMARY_BLUE, 
                   font=("Segoe UI", 16, "bold"))
    style.configure("Subtitle.TLabel", 
                   background=SOFT_BLUE, 
                   foreground=MEDIUM_GRAY, 
                   font=("Segoe UI", 12))
    
    # Configurar botones con colores educativos
    style.configure("TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=LIGHT_BLUE,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("TButton",
              background=[('active', PRIMARY_BLUE),
                         ('pressed', PRIMARY_BLUE)])
    
    # Botón de guardar (verde académico)
    style.configure("Save.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=ACADEMIC_GREEN,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("Save.TButton",
              background=[('active', LIGHT_GREEN),
                         ('pressed', LIGHT_GREEN)])
    
    # Botón de eliminar (rojo)
    style.configure("Delete.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=ERROR_RED,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("Delete.TButton",
              background=[('active', '#dc2626'),
                         ('pressed', '#dc2626')])
    
    # Botón de editar (azul)
    style.configure("Edit.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=LIGHT_BLUE,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("Edit.TButton",
              background=[('active', PRIMARY_BLUE),
                         ('pressed', PRIMARY_BLUE)])
    
    # Botón de salir (gris)
    style.configure("Exit.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=MEDIUM_GRAY,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("Exit.TButton",
              background=[('active', DARK_GRAY),
                         ('pressed', DARK_GRAY)])
    
    # Botón de logout (naranja)
    style.configure("Logout.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=WARNING_ORANGE,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("Logout.TButton",
              background=[('active', '#d97706'),
                         ('pressed', '#d97706')])
    
    # Botón de información (azul claro)
    style.configure("Info.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   background=INFO_BLUE,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[15, 8])
    style.map("Info.TButton",
              background=[('active', PRIMARY_BLUE),
                         ('pressed', PRIMARY_BLUE)])
    
    # Botón grande
    style.configure("Large.TButton", 
                   font=("Segoe UI", 12, "bold"),
                   background=LIGHT_BLUE,
                   foreground=WHITE,
                   borderwidth=0,
                   focuscolor='none',
                   padding=[20, 12])
    style.map("Large.TButton",
              background=[('active', PRIMARY_BLUE),
                         ('pressed', PRIMARY_BLUE)])
    
    # Configurar campos de entrada con estilo moderno
    style.configure("TEntry", 
                   font=("Segoe UI", 11),
                   fieldbackground=WHITE,
                   foreground=DARK_GRAY,
                   borderwidth=2,
                   relief="solid",
                   padding=[10, 8])
    style.map("TEntry",
              focuscolor=[('!focus', LIGHT_BLUE)],
              bordercolor=[('focus', PRIMARY_BLUE),
                          ('!focus', LIGHT_GRAY)])
    
    # Estilo especial para campos de login
    style.configure("Login.TEntry", 
                   font=("Segoe UI", 12),
                   fieldbackground=WHITE,
                   foreground=DARK_GRAY,
                   borderwidth=2,
                   relief="solid",
                   padding=[12, 10])
    style.map("Login.TEntry",
              focuscolor=[('!focus', LIGHT_BLUE)],
              bordercolor=[('focus', PRIMARY_BLUE),
                          ('!focus', '#d1d5db')])
    
    # Configurar comboboxes
    style.configure("TCombobox", 
                   font=("Segoe UI", 10),
                   fieldbackground=WHITE,
                   foreground=DARK_GRAY,
                   borderwidth=2,
                   relief="solid")
    style.map("TCombobox",
              focuscolor=[('!focus', LIGHT_BLUE)],
              bordercolor=[('focus', PRIMARY_BLUE),
                          ('!focus', LIGHT_GRAY)])
    
    # Configurar treeviews (tablas) con estilo profesional
    style.configure("Treeview", 
                   font=("Segoe UI", 10),
                   background=WHITE,
                   foreground=DARK_GRAY,
                   fieldbackground=WHITE,
                   borderwidth=1,
                   relief="solid")
    style.configure("Treeview.Heading", 
                   font=("Segoe UI", 10, "bold"),
                   background=PRIMARY_BLUE,
                   foreground=WHITE,
                   borderwidth=0,
                   relief="flat")
    style.map("Treeview.Heading",
              background=[('active', LIGHT_BLUE)])
    
    # Configurar scrollbars
    style.configure("TScrollbar", 
                   background=LIGHT_GRAY,
                   troughcolor=SOFT_BLUE,
                   borderwidth=0,
                   arrowcolor=MEDIUM_GRAY,
                   darkcolor=LIGHT_GRAY,
                   lightcolor=LIGHT_GRAY)
    
    # Maximiza/ajusta a pantalla disponible
    try:
        root.state("zoomed")  # Windows
    except Exception:
        pass
    # Fallback para Linux/Mac: usar geometry con pantalla completa
    try:
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry(f"{width}x{height}+0+0")
    except Exception:
        root.geometry("900x600")

    # Notebook principal con todas las pestañas
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Variables para controlar el estado de las pestañas
    login_tab_index = 0
    ingresos_tab_index = 1
    usuarios_tab_index = 2
    consultas_tab_index = 3
    current_usuario_id = None

    def on_logout_callback() -> None:
        nonlocal current_usuario_id
        
        # Limpiar usuario actual
        current_usuario_id = None
        
        # Habilitar pestaña de login y deshabilitar otras
        notebook.tab(login_tab_index, state="normal")
        if len(notebook.tabs()) > ingresos_tab_index:
            notebook.tab(ingresos_tab_index, state="disabled")
        if len(notebook.tabs()) > usuarios_tab_index:
            notebook.tab(usuarios_tab_index, state="disabled")
        if len(notebook.tabs()) > consultas_tab_index:
            notebook.tab(consultas_tab_index, state="disabled")
        
        # Cambiar a la pestaña de login
        notebook.select(login_tab_index)
        
        # Limpiar campos del login
        login_frame = notebook.nametowidget(notebook.tabs()[login_tab_index])
        if hasattr(login_frame, '_clear_fields'):
            login_frame._clear_fields()

    def on_login_success(usuario_id: int) -> None:
        nonlocal current_usuario_id
        
        # Guardar el usuario actual
        current_usuario_id = usuario_id
        
        # Obtener rol del usuario
        user_role = get_user_role(usuario_id, "academia.db")
        
        # Eliminar todas las pestañas excepto la de login
        tabs_to_remove = []
        for i in range(len(notebook.tabs())):
            if i != login_tab_index:  # No eliminar la pestaña de login
                tabs_to_remove.append(i)
        
        # Eliminar pestañas en orden inverso para evitar problemas de índices
        for i in reversed(tabs_to_remove):
            notebook.forget(i)
        
        # Crear pestañas según permisos del usuario actual
        current_tab_index = 1  # Empezar después de la pestaña de login
        
        # Crear pestaña de ingresos solo si tiene permiso
        if has_tab_permission(usuario_id, "ingresos", "academia.db"):
            ingresos_tab = create_ingresos_tab(notebook, usuario_id, on_logout_callback)
            notebook.add(ingresos_tab, text="Ingresos")
            current_tab_index += 1
        
        # Crear pestaña de consultas solo si tiene permiso
        if has_tab_permission(usuario_id, "consultas", "academia.db"):
            consultas_tab = create_consultas_tab(notebook, on_logout_callback)
            notebook.add(consultas_tab, text="Consultas")
            current_tab_index += 1
        
        # Crear pestaña de usuarios solo si tiene permiso
        if has_tab_permission(usuario_id, "registro_usuarios", "academia.db"):
            usuarios_tab = create_usuarios_tab(notebook, on_logout_callback)
            notebook.add(usuarios_tab, text="Usuarios")
            current_tab_index += 1
        
        # Deshabilitar pestaña de login
        notebook.tab(login_tab_index, state="disabled")
        
        # Habilitar todas las pestañas creadas (ya están habilitadas por defecto)
        for i in range(1, len(notebook.tabs())):
            notebook.tab(i, state="normal")
        
        # Cambiar a la primera pestaña disponible (la primera después del login)
        if len(notebook.tabs()) > 1:
            notebook.select(1)  # Seleccionar la primera pestaña después del login

    # Crear pestaña de login
    login_frame = create_login_frame(notebook, on_login_success)
    notebook.add(login_frame, text="Login")
    
    # Inicialmente solo habilitar la pestaña de login
    notebook.select(login_tab_index)

    return root


def main() -> None:
    root = create_main_window()
    root.mainloop()


if __name__ == "__main__":
    main()
