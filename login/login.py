import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

try:
    from ingresos.ingresos_db import authenticate_user
except Exception:
    def authenticate_user(usuario: str, contrasena: str, db_path: str = "academia.db") -> int | None:  # type: ignore
        return None


class LoginView(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_success):
        super().__init__(parent)
        self.on_success = on_success

        # Configurar el fondo principal
        self.configure(style="TFrame")

        # Contenedor principal con diseño de tarjeta elevada
        self._main_container = ttk.Frame(self, style="LoginCard.TFrame")
        self._main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Padding interno para la tarjeta
        self._card_padding = ttk.Frame(self._main_container)
        self._card_padding.pack(padx=40, pady=40)

        # Imagen/Logo
        self._image_label = ttk.Label(self._card_padding)
        self._image_label.pack(pady=(0, 20))
        self._load_image()

        # Título principal
        title_label = ttk.Label(self._card_padding, text="Sistema Académico", style="Title.TLabel")
        title_label.pack(pady=(0, 8))
        
        # Subtítulo
        subtitle_label = ttk.Label(self._card_padding, text="Iniciar Sesión", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 30))

        # Contenedor para los campos de entrada
        self._fields_container = ttk.Frame(self._card_padding)
        self._fields_container.pack(fill=tk.X, pady=(0, 20))

        # Campo de usuario
        user_label = ttk.Label(self._fields_container, text="Usuario:", style="TLabel")
        user_label.pack(anchor="w", pady=(0, 5))
        
        self.entry_usuario = ttk.Entry(self._fields_container, width=30, style="Login.TEntry")
        self._init_placeholder(self.entry_usuario, "Ingrese su usuario")
        self.entry_usuario.pack(fill=tk.X, pady=(0, 15), ipady=12)

        # Campo de contraseña
        password_label = ttk.Label(self._fields_container, text="Contraseña:", style="TLabel")
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.entry_contrasena = ttk.Entry(self._fields_container, width=30, show="", style="Login.TEntry")
        self._init_placeholder(self.entry_contrasena, "Ingrese su contraseña")
        self.entry_contrasena.pack(fill=tk.X, pady=(0, 20), ipady=12)

        # Contenedor para botones
        self._buttons_container = ttk.Frame(self._card_padding)
        self._buttons_container.pack(fill=tk.X)
        
        # Configurar columnas para centrar botones
        self._buttons_container.columnconfigure(0, weight=1)
        self._buttons_container.columnconfigure(1, weight=1)

        # Botones con mejor espaciado
        login_btn = ttk.Button(self._buttons_container, text="Iniciar Sesión", 
                              command=self._on_ingresar, style="Save.TButton")
        login_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=12)

        exit_btn = ttk.Button(self._buttons_container, text="Salir", 
                             command=self._on_salir, style="Exit.TButton")
        exit_btn.grid(row=0, column=1, sticky="ew", ipady=12)

        # Mensaje de bienvenida
        welcome_label = ttk.Label(self._card_padding, 
                                 text="Bienvenido al Sistema de Gestión Académica", 
                                 style="Subtitle.TLabel")
        welcome_label.pack(pady=(20, 0))

    def _load_image(self) -> None:
        try:
            # Cargar PNG simple con PhotoImage (soporta GIF/PGM/PPM/PNG en Tcl 8.6+)
            if Path("login/logo-inicio-sesion.png").exists():
                self._photo = tk.PhotoImage(file="login/logo-inicio-sesion.png")
                # Redimensionar a ~120x120 manteniendo proporciones
                try:
                    w, h = self._photo.width(), self._photo.height()
                    if w > 0 and h > 0:
                        # Calcular escala para que la imagen sea aproximadamente 120x120
                        scale_w = max(1, round(w / 120))
                        scale_h = max(1, round(h / 120))
                        self._photo = self._photo.subsample(scale_w, scale_h)
                except Exception:
                    pass
                self._image_label.configure(image=self._photo)
            else:
                # Si no existe la imagen, mostrar un icono educativo más elegante
                self._image_label.configure(text="🎓", font=("Segoe UI Emoji", 64))
        except Exception as e:
            # En caso de error, mostrar icono educativo
            self._image_label.configure(text="🎓", font=("Segoe UI Emoji", 64))

    def _init_placeholder(self, entry: ttk.Entry, placeholder: str) -> None:
        entry.insert(0, placeholder)
        entry.configure(foreground="#6b7280")  # Color gris más suave

        def on_focus_in(event: tk.Event) -> None:
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(foreground="#1f2937")  # Color de texto principal
                if "contraseña" in placeholder.lower() or "contrasena" in placeholder.lower():
                    entry.configure(show="*")

        def on_focus_out(event: tk.Event) -> None:
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(foreground="#6b7280")  # Color gris suave
                if "contraseña" in placeholder.lower() or "contrasena" in placeholder.lower():
                    entry.configure(show="")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _clear_fields(self) -> None:
        """Limpia los campos de usuario y contraseña."""
        # Limpiar campo de usuario
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, "Ingrese su usuario")
        self.entry_usuario.configure(foreground="#6b7280")
        
        # Limpiar campo de contraseña
        self.entry_contrasena.delete(0, tk.END)
        self.entry_contrasena.insert(0, "Ingrese su contraseña")
        self.entry_contrasena.configure(foreground="#6b7280", show="")

    def _on_ingresar(self) -> None:
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        # Si aún están los placeholders, tratar como vacío
        if usuario.lower() in ["usuario", "ingrese su usuario"]:
            usuario = ""
        if contrasena.lower() in ["contrasena", "contraseña", "ingrese su contraseña"]:
            contrasena = ""
        if not usuario or not contrasena:
            messagebox.showerror("Error", "Por favor, ingrese usuario y contraseña")
            return
        user_id = authenticate_user(usuario, contrasena, "academia.db")
        if user_id is not None:
            # Limpiar campos antes de proceder
            self._clear_fields()
            self.on_success(user_id)
        else:
            # Feedback visual y diálogo
            self.entry_usuario.configure(foreground="#ef4444")  # Rojo de error
            self.entry_contrasena.configure(foreground="#ef4444")  # Rojo de error
            messagebox.showerror("Credenciales inválidas", "Usuario o contraseña incorrectos. Por favor, verifique sus datos.")

    def _on_salir(self) -> None:
        self.winfo_toplevel().destroy()


def create_login_frame(parent: tk.Widget, on_success):
    return LoginView(parent, on_success)


