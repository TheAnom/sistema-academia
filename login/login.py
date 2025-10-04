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

        # Configurar estilo para botones grandes
        style = ttk.Style()
        style.configure("Large.TButton", 
                       font=("Segoe UI", 18),
                       background="#555", 
                       foreground="white")
        style.map("Large.TButton",
                  background=[("active", "#666"), ("pressed", "#444")])

        self._center_container = ttk.Frame(self)
        self._center_container.place(relx=0.5, rely=0.5, anchor="center")

        # Imagen
        self._image_label = ttk.Label(self._center_container)
        self._image_label.pack(pady=(0, 8))
        self._load_image()

        # Título
        ttk.Label(self._center_container, text="Login", font=("Segoe UI", 24, "bold")).pack(pady=(0, 8))

        # Inputs
        self.entry_usuario = ttk.Entry(self._center_container, width=30, font=("Segoe UI", 18))
        self._init_placeholder(self.entry_usuario, "Usuario")
        self.entry_usuario.pack(pady=6, ipady=8)

        self.entry_contrasena = ttk.Entry(self._center_container, width=30, show="", font=("Segoe UI", 18))
        self._init_placeholder(self.entry_contrasena, "Contrasena")
        self.entry_contrasena.pack(pady=6, ipady=8)

        # Botones
        btns = ttk.Frame(self._center_container)
        btns.pack(fill=tk.X, pady=(8, 0))
        # Centrado horizontal
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        ttk.Button(btns, text="Ingresar", command=self._on_ingresar, style="Save.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=8)
        ttk.Button(btns, text="Salir", command=self._on_salir, style="Exit.TButton").grid(row=0, column=1, sticky="ew", ipady=8)

    def _load_image(self) -> None:
        try:
            # Cargar PNG simple con PhotoImage (soporta GIF/PGM/PPM/PNG en Tcl 8.6+)
            if Path("login/logo-inicio-sesion.png").exists():
                self._photo = tk.PhotoImage(file="login/logo-inicio-sesion.png")
                # Redimensionar a ~100x100 manteniendo lo posible
                try:
                    w, h = self._photo.width(), self._photo.height()
                    if w > 0 and h > 0:
                        scale_w = max(1, round(w / 280))
                        scale_h = max(1, round(h / 280))
                        self._photo = self._photo.subsample(scale_w, scale_h)
                except Exception:
                    pass
                self._image_label.configure(image=self._photo)
            else:
                # Si no existe la imagen, mostrar un placeholder
                self._image_label.configure(text="👤", font=("Arial", 48))
        except Exception as e:
            # En caso de error, mostrar placeholder
            self._image_label.configure(text="👤", font=("Arial", 48))

    def _init_placeholder(self, entry: ttk.Entry, placeholder: str) -> None:
        entry.insert(0, placeholder)
        entry.configure(foreground="#888")

        def on_focus_in(event: tk.Event) -> None:
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(foreground="#000")
                if placeholder.lower().startswith("contrasena"):
                    entry.configure(show="*")

        def on_focus_out(event: tk.Event) -> None:
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(foreground="#888")
                if placeholder.lower().startswith("contrasena"):
                    entry.configure(show="")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _clear_fields(self) -> None:
        """Limpia los campos de usuario y contraseña."""
        # Limpiar campo de usuario
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, "Usuario")
        self.entry_usuario.configure(foreground="#888")
        
        # Limpiar campo de contraseña
        self.entry_contrasena.delete(0, tk.END)
        self.entry_contrasena.insert(0, "Contrasena")
        self.entry_contrasena.configure(foreground="#888", show="")

    def _on_ingresar(self) -> None:
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        # Si aún están los placeholders, tratar como vacío
        if usuario.lower() == "usuario":
            usuario = ""
        if contrasena.lower() == "contrasena":
            contrasena = ""
        if not usuario or not contrasena:
            messagebox.showerror("Error", "Ingrese usuario y contraseña")
            return
        user_id = authenticate_user(usuario, contrasena, "academia.db")
        if user_id is not None:
            # Limpiar campos antes de proceder
            self._clear_fields()
            self.on_success(user_id)
        else:
            # Feedback visual y diálogo
            self.entry_usuario.configure(foreground="#b00")
            self.entry_contrasena.configure(foreground="#b00")
            messagebox.showerror("Credenciales inválidas", "Usuario o contraseña incorrectos")

    def _on_salir(self) -> None:
        self.winfo_toplevel().destroy()


def create_login_frame(parent: tk.Widget, on_success):
    return LoginView(parent, on_success)


