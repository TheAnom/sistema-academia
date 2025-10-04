import tkinter as tk
from tkinter import ttk
from typing import List

from usuarios.usuarios_db import (
    fetch_roles_with_ids,
    fetch_usuarios_for_table,
    fetch_usuario_by_id,
    insert_usuario,
    update_usuario,
    delete_usuario,
)


class UsuariosView(ttk.Frame):
    """Vista para la gestión de usuarios."""

    def __init__(self, parent: tk.Widget, on_logout_callback=None):
        super().__init__(parent)
        self.on_logout_callback = on_logout_callback
        
        # Configurar estilo para botones con fuente 14
        style = ttk.Style()
        style.configure("Large.TButton", 
                       font=("Segoe UI", 14),
                       background="#555", 
                       foreground="white")
        style.map("Large.TButton",
                  background=[("active", "#666"), ("pressed", "#444")])
        
        # Configurar fuente para Treeview (tablas)
        style.configure("Large.TTreeview", 
                       font=("Segoe UI", 14), 
                       rowheight=35,
                       background="#444", 
                       foreground="white",
                       fieldbackground="#444")
        style.configure("Large.TTreeview.Heading", 
                       font=("Segoe UI", 14, "bold"),
                       background="#555", 
                       foreground="white")
        
        # Configure the frame to expand and fill the available space
        self.pack(fill=tk.BOTH, expand=True)

        self._build_header()
        self._build_layout()
        self._build_formulario(self.left_col)
        self._build_tabla(self.right_col)

    def _build_header(self) -> None:
        """Construye el encabezado."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=12, pady=12)
        ttk.Label(header, text="Gestión Usuario", font=("Segoe UI", 32, "bold")).pack()

    def _build_layout(self) -> None:
        """Construye el layout principal con dos columnas."""
        # Frame principal con dos columnas
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)  # Configurar fila para expandir en altura

        # Columna izquierda - Formulario
        self.left_col = ttk.Frame(main_frame)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Columna derecha - Tabla
        self.right_col = ttk.Frame(main_frame)
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

    def _build_formulario(self, parent: ttk.Frame) -> None:
        """Construye el formulario de gestión de usuarios."""
        # Frame centrado para el formulario
        form_frame = ttk.Frame(parent)
        form_frame.pack(expand=True, fill=tk.BOTH)
        
        # Frame interno para centrar el contenido
        center_frame = ttk.Frame(form_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título "Administración"
        ttk.Label(center_frame, text="Administración", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        # Inputs del formulario
        inputs_frame = ttk.Frame(center_frame)
        inputs_frame.pack(pady=(0, 20))

        # Nombre
        ttk.Label(inputs_frame, text="Nombre:", font=("Segoe UI", 14)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nombre = ttk.Entry(inputs_frame, width=25, font=("Segoe UI", 14))
        self.entry_nombre.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0), ipady=8)

        # Contraseña
        ttk.Label(inputs_frame, text="Contraseña:", font=("Segoe UI", 14)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_contrasena = ttk.Entry(inputs_frame, width=25, show="*", font=("Segoe UI", 14))
        self.entry_contrasena.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0), ipady=8)

        # Rol
        ttk.Label(inputs_frame, text="Rol:", font=("Segoe UI", 14)).grid(row=2, column=0, sticky="w", pady=5)
        self.combo_rol = ttk.Combobox(inputs_frame, width=22, state="readonly", font=("Segoe UI", 14))
        self.combo_rol.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0), ipady=8)

        # Configurar columnas
        inputs_frame.columnconfigure(1, weight=1)

        # Cargar roles
        self._load_roles()

        # Botones
        buttons_frame = ttk.Frame(center_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))

        # Configurar columnas para botones (3 columnas para mejor distribución)
        for i in range(3):
            buttons_frame.columnconfigure(i, weight=1)

        # Fila 1: Guardar, Eliminar, Guardar Cambios
        ttk.Button(buttons_frame, text="Guardar", command=self._on_guardar, style="Save.TButton").grid(row=0, column=0, sticky="ew", padx=2, pady=4, ipady=8)
        ttk.Button(buttons_frame, text="Eliminar", command=self._on_eliminar, style="Delete.TButton").grid(row=0, column=1, sticky="ew", padx=2, pady=4, ipady=8)
        ttk.Button(buttons_frame, text="Guardar Cambios", command=self._on_guardar_cambios, style="Edit.TButton").grid(row=0, column=2, sticky="ew", padx=2, pady=4, ipady=8)

        # Fila 2: Salir (centrado)
        ttk.Button(buttons_frame, text="Salir", command=self._on_salir, style="Exit.TButton").grid(row=1, column=0, columnspan=3, sticky="ew", padx=2, pady=4, ipady=8)

    def _build_tabla(self, parent: ttk.Frame) -> None:
        """Construye la tabla de usuarios."""
        # Frame principal para centrar la tabla
        main_table_frame = ttk.Frame(parent)
        main_table_frame.pack(expand=True, fill=tk.BOTH)
        
        # Frame para la tabla con altura fija
        table_frame = ttk.LabelFrame(main_table_frame, text="Usuarios")
        table_frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=250)

        # Configurar columnas de la tabla
        columns = ("num", "usuario_id", "nombre", "rol")
        self.tree_usuarios = ttk.Treeview(table_frame, columns=columns, show="headings", style="Large.Treeview")

        # Configurar encabezados
        self.tree_usuarios.heading("num", text="No.")
        self.tree_usuarios.heading("usuario_id", text="ID")
        self.tree_usuarios.heading("nombre", text="Nombre")
        self.tree_usuarios.heading("rol", text="Rol")

        # Configurar anchos de columnas
        self.tree_usuarios.column("num", width=50, anchor="center")
        self.tree_usuarios.column("usuario_id", width=60, anchor="center")
        self.tree_usuarios.column("nombre", width=250, anchor="w")
        self.tree_usuarios.column("rol", width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scrollbar
        self.tree_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Cargar datos
        self._load_usuarios_table()

        # Bind para selección
        self.tree_usuarios.bind("<<TreeviewSelect>>", self._on_usuario_select)

    def _load_roles(self) -> None:
        """Carga los roles en el combobox."""
        roles = fetch_roles_with_ids("academia.db")
        self._rol_ids = [rol_id for rol_id, _ in roles]
        self._rol_nombres = [nombre for _, nombre in roles]
        
        self.combo_rol['values'] = self._rol_nombres
        if self._rol_nombres:
            self.combo_rol.current(0)

    def _load_usuarios_table(self) -> None:
        """Carga los usuarios en la tabla."""
        for row in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(row)
        
        rows = fetch_usuarios_for_table("academia.db")
        for idx, (usuario_id, nombre, rol) in enumerate(rows, start=1):
            self.tree_usuarios.insert("", tk.END, iid=str(usuario_id), values=(idx, usuario_id, nombre, rol))

    def _get_selected_rol_id(self) -> int:
        """Obtiene el ID del rol seleccionado."""
        try:
            nombre = self.combo_rol.get()
            idx = self._rol_nombres.index(nombre)
            return self._rol_ids[idx]
        except (ValueError, IndexError):
            return 0

    def _get_selected_usuario_id(self) -> int:
        """Obtiene el ID del usuario seleccionado."""
        selection = self.tree_usuarios.selection()
        if not selection:
            return 0
        try:
            return int(selection[0])
        except ValueError:
            return 0

    def _clear_inputs(self) -> None:
        """Limpia los inputs del formulario."""
        self.entry_nombre.delete(0, tk.END)
        self.entry_contrasena.delete(0, tk.END)
        if self._rol_nombres:
            self.combo_rol.current(0)

    def _on_usuario_select(self, event: tk.Event) -> None:
        """Maneja la selección de un usuario en la tabla."""
        usuario_id = self._get_selected_usuario_id()
        if usuario_id <= 0:
            return
        
        data = fetch_usuario_by_id(usuario_id, "academia.db")
        if not data:
            return
        
        nombre, contrasena, rol_id = data
        
        # Llenar inputs
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, nombre)
        self.entry_contrasena.delete(0, tk.END)
        self.entry_contrasena.insert(0, contrasena)
        
        # Seleccionar rol
        try:
            idx = self._rol_ids.index(rol_id)
            self.combo_rol.current(idx)
        except ValueError:
            if self._rol_nombres:
                self.combo_rol.current(0)

    def _on_guardar(self) -> None:
        """Guarda un nuevo usuario."""
        nombre = self.entry_nombre.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        rol_id = self._get_selected_rol_id()
        
        if not nombre or not contrasena:
            return
        
        new_id = insert_usuario(nombre, contrasena, rol_id, "academia.db")
        if new_id:
            self._load_usuarios_table()
            self._clear_inputs()

    def _on_eliminar(self) -> None:
        """Elimina el usuario seleccionado."""
        usuario_id = self._get_selected_usuario_id()
        if usuario_id <= 0:
            return
        
        ok = delete_usuario(usuario_id, "academia.db")
        if ok:
            self._load_usuarios_table()
            self._clear_inputs()


    def _on_guardar_cambios(self) -> None:
        """Guarda los cambios del usuario seleccionado."""
        usuario_id = self._get_selected_usuario_id()
        if usuario_id <= 0:
            return
        
        nombre = self.entry_nombre.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        rol_id = self._get_selected_rol_id()
        
        if not nombre or not contrasena:
            return
        
        ok = update_usuario(usuario_id, nombre, contrasena, rol_id, "academia.db")
        if ok:
            self._load_usuarios_table()
            self._clear_inputs()

    def _on_salir(self) -> None:
        """Cierra la aplicación."""
        self.winfo_toplevel().destroy()