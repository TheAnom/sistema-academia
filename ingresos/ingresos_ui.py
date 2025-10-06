import tkinter as tk
from tkinter import ttk
from typing import List

from ingresos.ingresos_db import (
    fetch_grados_with_ids,
    fetch_conceptos_pago_with_ids,
    fetch_estudiantes_for_table,
    fetch_pagos_for_table,
    fetch_estudiante_by_id,
    insert_estudiante,
    update_estudiante,
    insert_pago,
    fetch_pago_by_id,
    update_pago,
    insert_calificacion,
    update_calificacion,
    fetch_calificacion_by_estudiante,
    delete_calificacion,
    delete_pago,
    delete_estudiante_cascade,
)

# Importar sistema de permisos
try:
    from permissions import has_action_permission
except ImportError:
    def has_action_permission(usuario_id: int, action: str, db_path: str = "academia.db") -> bool:
        return True  # Fallback: permitir todo si no hay sistema de permisos


class IngresosView(ttk.Frame):
    """Vista base para la pestaña de Ingresos.

    Por ahora solo muestra un encabezado y placeholders. Más adelante se
    agregarán formularios, tablas y acciones.
    """

    def __init__(self, parent: tk.Widget, usuario_id: int | None = None, on_logout_callback=None):
        super().__init__(parent)
        self._usuario_id = usuario_id or 0
        self.on_logout_callback = on_logout_callback

        # Los estilos de botones se configuran globalmente en main.py
        style = ttk.Style()
        
        # Configurar solo fuente para inputs - sin colores de fondo
        style.configure("Large.TEntry", font=("Segoe UI", 18))
        style.configure("Large.TCombobox", font=("Segoe UI", 18))
        
        # Configurar solo fuente para Treeview (tablas) - sin colores de fondo
        style.configure("Large.Treeview", font=("Segoe UI", 18), rowheight=40)
        style.configure("Large.Treeview.Heading", font=("Segoe UI", 18, "bold"))
        
        # Variables para filtros de tablas
        self._all_students_data: List[tuple] = []
        self._all_payments_data: List[tuple] = []

        self._build_header()
        self._build_layout()
        self._build_section_datos_estudiante(self.left_center_frame)
        self._build_section_ingreso_pagos(self.left_center_frame)
        self._build_section_ingresos_notas(self.left_center_frame)
        self._build_actions(self.left_center_frame)
        self._build_right_column(self.right_col)

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=16, pady=12)

        title = ttk.Label(header, text="Ingresos", font=("Segoe UI", 18, "bold"))
        title.pack(side=tk.LEFT)

    def _build_layout(self) -> None:
        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.left_col = ttk.Frame(body)
        self.right_col = ttk.Frame(body)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        # Crear frame de centrado para la columna izquierda
        self.left_center_frame = ttk.Frame(self.left_col)
        self.left_center_frame.place(relx=0.5, rely=0.5, anchor="center")

    def _build_right_column(self, parent: ttk.Frame) -> None:
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        # Sección 1: Tabla de Estudiantes (mitad superior)
        students_section = ttk.Frame(parent)
        students_section.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        
        # Título de la sección
        students_title = ttk.Label(students_section, text="Estudiantes", font=("Segoe UI", 20, "bold"))
        students_title.pack(anchor="w", pady=(0, 8))
        
        # Frame para búsqueda de estudiantes
        students_search_frame = ttk.Frame(students_section)
        students_search_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(students_search_frame, text="Buscar:", font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))
        self.students_search_entry = ttk.Entry(students_search_frame, width=15)
        self.students_search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.students_search_entry.bind("<KeyRelease>", self._on_students_search)
        
        ttk.Button(students_search_frame, text="Limpiar", command=self._clear_students_search, 
                  width=12).pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para la tabla
        students_table_frame = ttk.Frame(students_section)
        students_table_frame.pack(fill=tk.BOTH, expand=True)

        columns_students = ("num", "nombre", "institucion", "grado", "telefono")
        self.tree_students = ttk.Treeview(
            students_table_frame, columns=columns_students, show="headings", style="Large.Treeview"
        )
        self.tree_students.heading("num", text="No.")
        self.tree_students.heading("nombre", text="Nombre")
        self.tree_students.heading("institucion", text="Institución")
        self.tree_students.heading("grado", text="Grado")
        self.tree_students.heading("telefono", text="Teléfono")
        self.tree_students.column("num", width=40, anchor="center")
        self.tree_students.column("nombre", width=180, anchor="w")
        self.tree_students.column("institucion", width=140, anchor="w")
        self.tree_students.column("grado", width=100, anchor="center")
        self.tree_students.column("telefono", width=110, anchor="center")
        self.tree_students.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._load_students_table()
        self.tree_students.bind("<<TreeviewSelect>>", self._on_student_select)
        
        # Bind para deseleccionar al hacer clic fuera
        self.tree_students.bind("<Button-1>", self._on_tree_click)

        # Sección 2: Tabla de Pagos (mitad inferior)
        payments_section = ttk.Frame(parent)
        payments_section.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        
        # Título de la sección
        payments_title = ttk.Label(payments_section, text="Pagos", font=("Segoe UI", 14, "bold"))
        payments_title.pack(anchor="w", pady=(0, 8))
        
        # Frame para búsqueda de pagos
        payments_search_frame = ttk.Frame(payments_section)
        payments_search_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(payments_search_frame, text="Buscar:", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, 5))
        self.payments_search_entry = ttk.Entry(payments_search_frame, style="Large.TEntry", width=20)
        self.payments_search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.payments_search_entry.bind("<KeyRelease>", self._on_payments_search)
        
        ttk.Button(payments_search_frame, text="Limpiar", command=self._clear_payments_search, 
                  width=15, style="Large.TButton").pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para la tabla
        payments_table_frame = ttk.Frame(payments_section)
        payments_table_frame.pack(fill=tk.BOTH, expand=True)

        columns_payments = ("num", "concepto", "estudiante", "ejecutor", "monto", "fecha")
        self.tree_payments = ttk.Treeview(
            payments_table_frame, columns=columns_payments, show="headings", style="Large.Treeview"
        )
        self.tree_payments.heading("num", text="No.")
        self.tree_payments.heading("concepto",text="Concepto")
        self.tree_payments.heading("estudiante", text="Estudiante")
        self.tree_payments.heading("ejecutor", text="Ejecutor")
        self.tree_payments.heading("monto", text="Monto")
        self.tree_payments.heading("fecha", text="Fecha")
        self.tree_payments.column("num", width=10, anchor="center")
        self.tree_payments.column("concepto", width=100, anchor="w")
        self.tree_payments.column("estudiante", width=140, anchor="w")
        self.tree_payments.column("ejecutor", width=80, anchor="w")
        self.tree_payments.column("monto", width=50, anchor="e")
        self.tree_payments.column("fecha", width=110, anchor="center")
        self.tree_payments.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._load_payments_table()
        self.tree_payments.bind("<<TreeviewSelect>>", self._on_payment_select)
        
        # Bind para deseleccionar al hacer clic fuera
        self.tree_payments.bind("<Button-1>", self._on_tree_click)

    def _build_section_datos_estudiante(self, parent: ttk.Frame) -> None:
        section = ttk.Frame(parent)
        section.pack(fill=tk.X, pady=(0, 12))
        
        # Título de la sección
        title_label = ttk.Label(section, text="Datos de Estudiante", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(section)
        content_frame.pack(fill=tk.X)

        # Configurar grilla para distribuir horizontalmente
        for col in range(2):
            content_frame.columnconfigure(col, weight=1)

        # Fila 0: Nombre | Apellido
        self.entry_nombre = ttk.Entry(content_frame, style="Large.TEntry")
        self._init_placeholder(self.entry_nombre, "Nombre")
        self.entry_nombre.grid(row=0, column=0, sticky="ew", padx=8, pady=6, ipady=8)

        self.entry_apellido = ttk.Entry(content_frame, style="Large.TEntry")
        self._init_placeholder(self.entry_apellido, "Apellido")
        self.entry_apellido.grid(row=0, column=1, sticky="ew", padx=8, pady=6, ipady=8)

        # Fila 1: Telefono | Grado (combobox)
        self.entry_telefono = ttk.Entry(content_frame, style="Large.TEntry")
        self._init_placeholder(self.entry_telefono, "Telefono")
        self.entry_telefono.grid(row=1, column=0, sticky="ew", padx=8, pady=6, ipady=8)

        self._grado_ids: List[int] = []
        self._grado_nombres: List[str] = []
        self._cargar_grados()
        self.combo_grado = ttk.Combobox(content_frame, values=self._grado_nombres, state="readonly", style="Large.TCombobox")
        # Default: grado_id = 1 si existe
        try:
            idx_default = self._grado_ids.index(1)
            self.combo_grado.current(idx_default)
        except ValueError:
            self.combo_grado.set("Seleccione grado")
        self.combo_grado.grid(row=1, column=1, sticky="ew", padx=8, pady=6, ipady=8)

        # Fila 2: Institucion (ocupa 2 columnas)
        self.entry_institucion = ttk.Entry(content_frame, style="Large.TEntry")
        self._init_placeholder(self.entry_institucion, "Institucion")
        self.entry_institucion.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=6, ipady=8)

    def _build_section_ingreso_pagos(self, parent: ttk.Frame) -> None:
        section = ttk.Frame(parent)
        section.pack(fill=tk.X, pady=(0, 12))
        
        # Título de la sección
        title_label = ttk.Label(section, text="Ingreso Pagos", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(section)
        content_frame.pack(fill=tk.X)

        row = ttk.Frame(content_frame)
        row.pack(anchor="w", padx=8, pady=6)

        # Concepto a cancelar (combobox) – horizontal, no expandir todo el ancho
        self._concepto_ids: List[int] = []
        self._concepto_nombres: List[str] = []
        self._cargar_conceptos_pago()
        self.combo_concepto = ttk.Combobox(row, values=self._concepto_nombres, state="readonly", width=28, style="Large.TCombobox")
        # Default: concepto_pago_id = 1 si existe
        try:
            idx_default = self._concepto_ids.index(1)
            self.combo_concepto.current(idx_default)
        except ValueError:
            self.combo_concepto.set("Concepto a cancelar")
        self.combo_concepto.pack(side=tk.LEFT, padx=(0, 8), ipady=8)

        # Monto (entry) – horizontal, ancho auto por contenido
        self.entry_monto = ttk.Entry(row, width=14, style="Large.TEntry")
        self._init_placeholder(self.entry_monto, "Monto")
        self.entry_monto.pack(side=tk.LEFT, ipady=8)

    def _build_section_ingresos_notas(self, parent: ttk.Frame) -> None:
        section = ttk.Frame(parent)
        section.pack(fill=tk.X, pady=(0, 12))
        
        # Título de la sección
        title_label = ttk.Label(section, text="Ingresos de Notas", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(section)
        content_frame.pack(fill=tk.X)

        # Distribución horizontal: Nota 1, 2, 3, 4
        row = ttk.Frame(content_frame)
        row.pack(anchor="w", padx=8, pady=6)

        self.entry_nota1 = ttk.Entry(row, width=10, style="Large.TEntry")
        self._init_placeholder(self.entry_nota1, "Nota 1")
        self.entry_nota1.pack(side=tk.LEFT, padx=(0, 8), ipady=8)

        self.entry_nota2 = ttk.Entry(row, width=10, style="Large.TEntry")
        self._init_placeholder(self.entry_nota2, "Nota 2")
        self.entry_nota2.pack(side=tk.LEFT, padx=(0, 8), ipady=8)

        self.entry_nota3 = ttk.Entry(row, width=10, style="Large.TEntry")
        self._init_placeholder(self.entry_nota3, "Nota 3")
        self.entry_nota3.pack(side=tk.LEFT, padx=(0, 8), ipady=8)

        self.entry_nota4 = ttk.Entry(row, width=10, style="Large.TEntry")
        self._init_placeholder(self.entry_nota4, "Nota 4")
        self.entry_nota4.pack(side=tk.LEFT, ipady=8)

    def _build_actions(self, parent: ttk.Frame) -> None:
        actions = ttk.Frame(parent)
        actions.pack(fill=tk.X, pady=(0, 12))
        
        # Título de la sección
        title_label = ttk.Label(actions, text="Acciones", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(actions)
        content_frame.pack(fill=tk.X)

        # Fila 1: Estudiante
        row1 = ttk.Frame(content_frame)
        row1.pack(fill=tk.X, padx=8, pady=4)
        for i in range(3):
            row1.columnconfigure(i, weight=1)
        
        # Botón Guardar Estudiante (siempre visible)
        ttk.Button(row1, text="Guardar Estudiante", command=self._on_guardar_estudiante, width=15, style="Save.TButton").grid(row=0, column=0, sticky="ew", padx=4)
        
        # Botón Modificar Estudiante (solo si tiene permiso)
        if has_action_permission(self._usuario_id, "Modificar Estudiantes", "academia.db"):
            self.btn_modificar_estudiante = ttk.Button(row1, text="Modificar Estudiante", command=self._on_modificar_estudiante, width=15, style="Edit.TButton")
            self.btn_modificar_estudiante.grid(row=0, column=1, sticky="ew", padx=4)
        else:
            # Crear botón deshabilitado
            self.btn_modificar_estudiante = ttk.Button(row1, text="Modificar Estudiante", state="disabled", width=15, style="Large.TButton")
            self.btn_modificar_estudiante.grid(row=0, column=1, sticky="ew", padx=4)
        
        # Botón Eliminar Estudiante (solo si tiene permiso)
        if has_action_permission(self._usuario_id, "Eliminar Estudiantes", "academia.db"):
            self.btn_eliminar_estudiante = ttk.Button(row1, text="Eliminar Estudiante", command=self._on_eliminar_estudiante, width=15, style="Delete.TButton")
            self.btn_eliminar_estudiante.grid(row=0, column=2, sticky="ew", padx=4)
        else:
            # Crear botón deshabilitado
            self.btn_eliminar_estudiante = ttk.Button(row1, text="Eliminar Estudiante", state="disabled", width=15, style="Large.TButton")
            self.btn_eliminar_estudiante.grid(row=0, column=2, sticky="ew", padx=4)

        # Fila 2: Pago
        row2 = ttk.Frame(content_frame)
        row2.pack(fill=tk.X, padx=8, pady=4)
        for i in range(3):
            row2.columnconfigure(i, weight=1)
        
        # Botón Guardar Pago (siempre visible)
        ttk.Button(row2, text="Guardar Pago", command=self._on_guardar_pago, width=15, style="Save.TButton").grid(row=0, column=0, sticky="ew", padx=4)
        
        # Botón Modificar Pago (solo si tiene permiso)
        if has_action_permission(self._usuario_id, "Modificar Pagos", "academia.db"):
            self.btn_modificar_pago = ttk.Button(row2, text="Modificar Pago", command=self._on_modificar_pago, width=15, style="Edit.TButton")
            self.btn_modificar_pago.grid(row=0, column=1, sticky="ew", padx=4)
        else:
            # Crear botón deshabilitado
            self.btn_modificar_pago = ttk.Button(row2, text="Modificar Pago", state="disabled", width=15, style="Large.TButton")
            self.btn_modificar_pago.grid(row=0, column=1, sticky="ew", padx=4)
        
        # Botón Eliminar Pago (solo si tiene permiso)
        if has_action_permission(self._usuario_id, "Eliminar Pagos", "academia.db"):
            self.btn_eliminar_pago = ttk.Button(row2, text="Eliminar Pago", command=self._on_eliminar_pago, width=15, style="Delete.TButton")
            self.btn_eliminar_pago.grid(row=0, column=2, sticky="ew", padx=4)
        else:
            # Crear botón deshabilitado
            self.btn_eliminar_pago = ttk.Button(row2, text="Eliminar Pago", state="disabled", width=15, style="Large.TButton")
            self.btn_eliminar_pago.grid(row=0, column=2, sticky="ew", padx=4)

        # Fila 3: Nota
        row3 = ttk.Frame(content_frame)
        row3.pack(fill=tk.X, padx=8, pady=4)
        for i in range(3):
            row3.columnconfigure(i, weight=1)
        
        # Botón Guardar Nota (siempre visible)
        ttk.Button(row3, text="Guardar Nota", command=self._on_guardar_nota, width=15, style="Save.TButton").grid(row=0, column=0, sticky="ew", padx=4)
        
        # Botón Modificar Nota (solo si tiene permiso)
        if has_action_permission(self._usuario_id, "Modificar Notas", "academia.db"):
            self.btn_modificar_nota = ttk.Button(row3, text="Modificar Nota", command=self._on_modificar_nota, width=15, style="Edit.TButton")
            self.btn_modificar_nota.grid(row=0, column=1, sticky="ew", padx=4)
        else:
            # Crear botón deshabilitado
            self.btn_modificar_nota = ttk.Button(row3, text="Modificar Nota", state="disabled", width=15, style="Large.TButton")
            self.btn_modificar_nota.grid(row=0, column=1, sticky="ew", padx=4)
        
        # Botón Eliminar Nota (solo si tiene permiso)
        if has_action_permission(self._usuario_id, "Eliminar Notas", "academia.db"):
            self.btn_eliminar_nota = ttk.Button(row3, text="Eliminar Nota", command=self._on_eliminar_nota, width=15, style="Delete.TButton")
            self.btn_eliminar_nota.grid(row=0, column=2, sticky="ew", padx=4)
        else:
            # Crear botón deshabilitado
            self.btn_eliminar_nota = ttk.Button(row3, text="Eliminar Nota", state="disabled", width=15, style="Large.TButton")
            self.btn_eliminar_nota.grid(row=0, column=2, sticky="ew", padx=4)

        # Fila 4: Sistema
        row4 = ttk.Frame(content_frame)
        row4.pack(fill=tk.X, padx=8, pady=4)
        for i in range(3):
            row4.columnconfigure(i, weight=1)
        ttk.Button(row4, text="Actualizar", command=self._on_actualizar_sistema, width=15, style="Large.TButton").grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(row4, text="Cerrar sesión", command=self._on_cerrar_sesion, width=15, style="Logout.TButton").grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(row4, text="Salir", command=self._on_salir, width=15, style="Exit.TButton").grid(row=0, column=2, sticky="ew", padx=4)

    def _get_selected_grado_id(self) -> int:
        try:
            nombre = self.combo_grado.get()
            idx = self._grado_nombres.index(nombre)
            return self._grado_ids[idx]
        except Exception:
            return 0

    def _on_guardar_estudiante(self) -> None:
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        telefono = self.entry_telefono.get().strip()
        institucion = self.entry_institucion.get().strip()
        grado_id = self._get_selected_grado_id()
        if not nombre or not apellido:
            return
        new_id = insert_estudiante(nombre, apellido, telefono, grado_id, institucion, "academia.db")
        if new_id:
            self._load_students_table()
            self._clear_student_inputs()
            self._deselect_all_tables()

    def _on_modificar_estudiante(self) -> None:
        selection = self.tree_students.selection()
        if not selection:
            return
        try:
            estudiante_id = int(selection[0])
        except ValueError:
            return
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        telefono = self.entry_telefono.get().strip()
        institucion = self.entry_institucion.get().strip()
        grado_id = self._get_selected_grado_id()
        if not nombre or not apellido:
            return
        ok = update_estudiante(estudiante_id, nombre, apellido, telefono, grado_id, institucion, "academia.db")
        if ok:
            self._load_students_table()
            self._clear_student_inputs()
            self._deselect_all_tables()

    def _get_selected_concepto_id(self) -> int:
        try:
            nombre = self.combo_concepto.get()
            idx = self._concepto_nombres.index(nombre)
            return self._concepto_ids[idx]
        except Exception:
            return 0

    def _get_selected_estudiante_id(self) -> int:
        selection = self.tree_students.selection()
        if not selection:
            return 0
        try:
            return int(selection[0])
        except ValueError:
            return 0

    def _on_guardar_pago(self) -> None:
        concepto_id = self._get_selected_concepto_id()
        estudiante_id = self._get_selected_estudiante_id()
        usuario_id = self._usuario_id
        try:
            monto = float(self.entry_monto.get().strip())
        except Exception:
            return
        if concepto_id <= 0 or estudiante_id <= 0 or usuario_id <= 0:
            return
        new_id = insert_pago(concepto_id, estudiante_id, usuario_id, monto, "academia.db")
        if new_id:
            self._load_payments_table()
            self.entry_monto.delete(0, tk.END)
            self._init_placeholder(self.entry_monto, "Monto")
            self._deselect_all_tables()

    def _on_payment_select(self, event: tk.Event) -> None:
        selection = self.tree_payments.selection()
        if not selection:
            return
        iid = selection[0]
        try:
            pago_id = int(iid)
        except ValueError:
            return
        data = fetch_pago_by_id(pago_id, "academia.db")
        if not data:
            return
        concepto_id, estudiante_id, monto, _ = data
        # Seleccionar concepto por id
        try:
            idx = self._concepto_ids.index(concepto_id)
            self.combo_concepto.current(idx)
        except ValueError:
            pass
        # Seleccionar estudiante en la tabla
        try:
            self.tree_students.selection_set(str(estudiante_id))
            self.tree_students.see(str(estudiante_id))
        except Exception:
            pass
        # Cargar monto
        self._set_entry_text(self.entry_monto, str(monto))

    def _on_modificar_pago(self) -> None:
        selection = self.tree_payments.selection()
        if not selection:
            return
        try:
            pago_id = int(selection[0])
        except ValueError:
            return
        concepto_id = self._get_selected_concepto_id()
        estudiante_id = self._get_selected_estudiante_id()
        usuario_id = self._usuario_id
        try:
            monto = float(self.entry_monto.get().strip())
        except Exception:
            return
        if pago_id <= 0 or concepto_id <= 0 or estudiante_id <= 0 or usuario_id <= 0:
            return
        ok = update_pago(pago_id, concepto_id, estudiante_id, usuario_id, monto, "academia.db")
        if ok:
            self._load_payments_table()
            self._deselect_all_tables()

    def _clear_student_inputs(self) -> None:
        for entry, placeholder in [
            (self.entry_nombre, "Nombre"),
            (self.entry_apellido, "Apellido"),
            (self.entry_telefono, "Telefono"),
            (self.entry_institucion, "Institucion"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.configure(foreground="#888")
        # Reset grado
        try:
            idx_default = self._grado_ids.index(1)
            self.combo_grado.current(idx_default)
        except ValueError:
            self.combo_grado.set("Seleccione grado")

    def _init_placeholder(self, entry: ttk.Entry, placeholder: str) -> None:
        entry.insert(0, placeholder)
        entry.configure(foreground="#888")

        def on_focus_in(event: tk.Event) -> None:
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(foreground="#000")

        def on_focus_out(event: tk.Event) -> None:
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(foreground="#888")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def _cargar_grados(self) -> None:
        data = fetch_grados_with_ids("academia.db")
        self._grado_ids = [item[0] for item in data]
        self._grado_nombres = [item[1] for item in data]

    def _cargar_conceptos_pago(self) -> None:
        data = fetch_conceptos_pago_with_ids("academia.db")
        self._concepto_ids = [item[0] for item in data]
        self._concepto_nombres = [item[1] for item in data]

    def _load_students_table(self) -> None:
        for row in self.tree_students.get_children():
            self.tree_students.delete(row)
        rows = fetch_estudiantes_for_table("academia.db")
        # Almacenar datos originales para filtros
        self._all_students_data = rows
        for idx, (estudiante_id, nombre, institucion, grado, telefono) in enumerate(rows, start=1):
            self.tree_students.insert("", tk.END, iid=str(estudiante_id), values=(idx, nombre, institucion, grado, telefono))

    def _load_payments_table(self) -> None:
        for row in self.tree_payments.get_children():
            self.tree_payments.delete(row)
        rows = fetch_pagos_for_table("academia.db")
        # Almacenar datos originales para filtros
        self._all_payments_data = rows
        for idx, (pago_id, concepto, estudiante, usuario, monto, fecha) in enumerate(rows, start=1):
            self.tree_payments.insert("", tk.END, iid=str(pago_id), values=(idx, concepto, estudiante, usuario, monto, fecha))

    def _on_salir(self) -> None:
        self.winfo_toplevel().destroy()

    def _on_actualizar_sistema(self) -> None:
        """Actualiza y refresca todos los datos del sistema."""
        try:
            # Mostrar mensaje de actualización
            from tkinter import messagebox
            messagebox.showinfo("Actualizando Sistema", "Refrescando todos los datos del sistema...")
            
            # Refrescar datos de grados
            self._cargar_grados()
            
            # Refrescar datos de conceptos de pago
            self._cargar_conceptos_pago()
            
            # Refrescar tabla de estudiantes
            self._load_students_table()
            
            # Refrescar tabla de pagos
            self._load_payments_table()
            
            # Limpiar todos los campos de entrada
            self._clear_student_inputs()
            self._clear_payment_inputs()
            self._clear_notas_inputs()
            
            # Deseleccionar todas las tablas
            self._deselect_all_tables()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Sistema Actualizado", "Todos los datos han sido refrescados exitosamente.")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al actualizar el sistema: {str(e)}")

    def _on_cerrar_sesion(self) -> None:
        """Regresa al login usando el callback del sistema de pestañas."""
        if self.on_logout_callback:
            self.on_logout_callback()

    def _on_tree_click(self, event: tk.Event) -> None:
        """Maneja clics en las tablas para deseleccionar si se hace clic fuera de una fila."""
        widget = event.widget
        # Verificar si el clic fue en una fila o en el área vacía
        item = widget.identify_row(event.y)
        if not item:
            # Clic fuera de una fila, deseleccionar
            widget.selection_remove(widget.selection())

    def _deselect_all_tables(self) -> None:
        """Deselecciona todas las tablas."""
        self.tree_students.selection_remove(self.tree_students.selection())
        self.tree_payments.selection_remove(self.tree_payments.selection())

    def _on_student_select(self, event: tk.Event) -> None:
        selection = self.tree_students.selection()
        if not selection:
            return
        iid = selection[0]
        try:
            estudiante_id = int(iid)
        except ValueError:
            return
        data = fetch_estudiante_by_id(estudiante_id, "academia.db")
        if not data:
            return
        nombre, apellido, institucion, grado_id, telefono = data
        self._set_entry_text(self.entry_nombre, nombre)
        self._set_entry_text(self.entry_apellido, apellido)
        self._set_entry_text(self.entry_telefono, telefono)
        self._set_entry_text(self.entry_institucion, institucion)
        # Seleccionar grado en combobox si existe
        try:
            idx = self._grado_ids.index(grado_id)
            self.combo_grado.current(idx)
        except ValueError:
            pass
        
        # Cargar notas del estudiante
        self._load_estudiante_notas(estudiante_id)

    def _set_entry_text(self, entry: ttk.Entry, text: str) -> None:
        entry.configure(foreground="#000")
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def _get_nota_value(self, entry: ttk.Entry) -> float:
        """Obtiene el valor de una nota, retorna 0.0 si está vacía o es placeholder."""
        text = entry.get().strip()
        if not text or text in ["Nota 1", "Nota 2", "Nota 3", "Nota 4"]:
            return 0.0
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _load_estudiante_notas(self, estudiante_id: int) -> None:
        """Carga las notas de un estudiante en los inputs."""
        data = fetch_calificacion_by_estudiante(estudiante_id, "academia.db")
        if data:
            _, nota_uno, nota_dos, nota_tres, nota_cuatro = data
            self._set_entry_text(self.entry_nota1, str(nota_uno))
            self._set_entry_text(self.entry_nota2, str(nota_dos))
            self._set_entry_text(self.entry_nota3, str(nota_tres))
            self._set_entry_text(self.entry_nota4, str(nota_cuatro))
        else:
            # Limpiar notas si no hay calificación
            self._clear_notas_inputs()

    def _clear_payment_inputs(self) -> None:
        """Limpia los inputs de pagos."""
        for entry, placeholder in [
            (self.entry_monto, "Monto"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.configure(foreground="#888")
        # Reset combo de concepto
        self.combo_concepto.set("Concepto a cancelar")

    def _clear_grade_inputs(self) -> None:
        """Limpia los inputs de notas."""
        for entry, placeholder in [
            (self.entry_nota1, "Nota 1"),
            (self.entry_nota2, "Nota 2"),
            (self.entry_nota3, "Nota 3"),
            (self.entry_nota4, "Nota 4"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.configure(foreground="#888")

    def _clear_notas_inputs(self) -> None:
        """Limpia los inputs de notas."""
        for entry, placeholder in [
            (self.entry_nota1, "Nota 1"),
            (self.entry_nota2, "Nota 2"),
            (self.entry_nota3, "Nota 3"),
            (self.entry_nota4, "Nota 4"),
        ]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.configure(foreground="#888")

    def _on_guardar_nota(self) -> None:
        """Guarda las notas de un estudiante."""
        estudiante_id = self._get_selected_estudiante_id()
        if estudiante_id <= 0:
            return
        
        nota_uno = self._get_nota_value(self.entry_nota1)
        nota_dos = self._get_nota_value(self.entry_nota2)
        nota_tres = self._get_nota_value(self.entry_nota3)
        nota_cuatro = self._get_nota_value(self.entry_nota4)
        
        # Verificar si ya existe una calificación para este estudiante
        existing = fetch_calificacion_by_estudiante(estudiante_id, "academia.db")
        if existing:
            # Actualizar calificación existente
            calificacion_id, _, _, _, _ = existing
            ok = update_calificacion(calificacion_id, nota_uno, nota_dos, nota_tres, nota_cuatro, "academia.db")
        else:
            # Insertar nueva calificación
            new_id = insert_calificacion(estudiante_id, nota_uno, nota_dos, nota_tres, nota_cuatro, "academia.db")
            ok = new_id is not None
        
        if ok:
            self._clear_notas_inputs()
            self._deselect_all_tables()

    def _on_modificar_nota(self) -> None:
        """Modifica las notas de un estudiante (igual que guardar, pero solo actualiza)."""
        estudiante_id = self._get_selected_estudiante_id()
        if estudiante_id <= 0:
            return
        
        # Verificar si existe una calificación para este estudiante
        existing = fetch_calificacion_by_estudiante(estudiante_id, "academia.db")
        if not existing:
            return  # No hay calificación para modificar
        
        nota_uno = self._get_nota_value(self.entry_nota1)
        nota_dos = self._get_nota_value(self.entry_nota2)
        nota_tres = self._get_nota_value(self.entry_nota3)
        nota_cuatro = self._get_nota_value(self.entry_nota4)
        
        calificacion_id, _, _, _, _ = existing
        ok = update_calificacion(calificacion_id, nota_uno, nota_dos, nota_tres, nota_cuatro, "academia.db")
        
        if ok:
            self._clear_notas_inputs()
            self._deselect_all_tables()

    def _on_eliminar_nota(self) -> None:
        """Elimina las notas de un estudiante."""
        estudiante_id = self._get_selected_estudiante_id()
        if estudiante_id <= 0:
            return
        
        # Verificar si existe una calificación para este estudiante
        existing = fetch_calificacion_by_estudiante(estudiante_id, "academia.db")
        if not existing:
            return  # No hay calificación para eliminar
        
        calificacion_id, _, _, _, _ = existing
        ok = delete_calificacion(calificacion_id, "academia.db")
        
        if ok:
            self._clear_notas_inputs()
            self._deselect_all_tables()

    def _on_eliminar_pago(self) -> None:
        """Elimina un pago seleccionado."""
        selection = self.tree_payments.selection()
        if not selection:
            return
        try:
            pago_id = int(selection[0])
        except ValueError:
            return
        
        ok = delete_pago(pago_id, "academia.db")
        if ok:
            self._load_payments_table()
            # Limpiar inputs de pago
            self.entry_monto.delete(0, tk.END)
            self._init_placeholder(self.entry_monto, "Monto")

    def _on_eliminar_estudiante(self) -> None:
        """Elimina un estudiante y todas sus relaciones."""
        selection = self.tree_students.selection()
        if not selection:
            return
        try:
            estudiante_id = int(selection[0])
        except ValueError:
            return
        
        ok = delete_estudiante_cascade(estudiante_id, "academia.db")
        if ok:
            # Recargar todas las tablas
            self._load_students_table()
            self._load_payments_table()
            # Limpiar todos los inputs
            self._clear_student_inputs()
            self._clear_notas_inputs()
            self.entry_monto.delete(0, tk.END)
            self._init_placeholder(self.entry_monto, "Monto")

    def _on_students_search(self, event: tk.Event) -> None:
        """Filtra la tabla de estudiantes por nombre."""
        search_text = self.students_search_entry.get().lower().strip()
        
        # Limpiar tabla
        for row in self.tree_students.get_children():
            self.tree_students.delete(row)
        
        if not search_text:
            # Mostrar todos los estudiantes
            for idx, (estudiante_id, nombre, institucion, grado, telefono) in enumerate(self._all_students_data, start=1):
                self.tree_students.insert("", tk.END, iid=str(estudiante_id), values=(idx, nombre, institucion, grado, telefono))
        else:
            # Filtrar por nombre
            filtered_data = []
            for estudiante_id, nombre, institucion, grado, telefono in self._all_students_data:
                if search_text in nombre.lower():
                    filtered_data.append((estudiante_id, nombre, institucion, grado, telefono))
            
            for idx, (estudiante_id, nombre, institucion, grado, telefono) in enumerate(filtered_data, start=1):
                self.tree_students.insert("", tk.END, iid=str(estudiante_id), values=(idx, nombre, institucion, grado, telefono))

    def _clear_students_search(self) -> None:
        """Limpia el campo de búsqueda de estudiantes y muestra todos los datos."""
        self.students_search_entry.delete(0, tk.END)
        self._on_students_search(None)

    def _on_payments_search(self, event: tk.Event) -> None:
        """Filtra la tabla de pagos por nombre del estudiante."""
        search_text = self.payments_search_entry.get().lower().strip()
        
        # Limpiar tabla
        for row in self.tree_payments.get_children():
            self.tree_payments.delete(row)
        
        if not search_text:
            # Mostrar todos los pagos
            for idx, (pago_id, concepto, estudiante, usuario, monto, fecha) in enumerate(self._all_payments_data, start=1):
                self.tree_payments.insert("", tk.END, iid=str(pago_id), values=(idx, concepto, estudiante, usuario, monto, fecha))
        else:
            # Filtrar por nombre del estudiante
            filtered_data = []
            for pago_id, concepto, estudiante, usuario, monto, fecha in self._all_payments_data:
                if search_text in estudiante.lower():
                    filtered_data.append((pago_id, concepto, estudiante, usuario, monto, fecha))
            
            for idx, (pago_id, concepto, estudiante, usuario, monto, fecha) in enumerate(filtered_data, start=1):
                self.tree_payments.insert("", tk.END, iid=str(pago_id), values=(idx, concepto, estudiante, usuario, monto, fecha))

    def _clear_payments_search(self) -> None:
        """Limpia el campo de búsqueda de pagos y muestra todos los datos."""
        self.payments_search_entry.delete(0, tk.END)
        self._on_payments_search(None)


