import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple

from consultas.consultas_db import (
    fetch_estudiantes_for_autocomplete,
    fetch_estudiante_complete_data,
    search_estudiantes_by_name,
    fetch_conceptos_pago_for_solvency,
    fetch_pagos_by_estudiante_and_concepto,
    check_solvency_status,
    fetch_exam_conceptos_pago,
    fetch_calificaciones_by_estudiante,
    calculate_average,
    is_approved,
)


class ConsultasView(ttk.Frame):
    """Vista para consultar datos de estudiantes."""

    def __init__(self, parent: tk.Widget, on_logout_callback=None):
        super().__init__(parent)
        self.on_logout_callback = on_logout_callback
        
        # Configure the frame to expand and fill the available space
        self.pack(fill=tk.BOTH, expand=True)
        
        # Los estilos de botones se configuran globalmente en main.py
        style = ttk.Style()
        
        # Configurar solo fuente para Treeview (tablas) - sin colores de fondo
        style.configure("Large.TTreeview", font=("Segoe UI", 14))
        style.configure("Large.TTreeview.Heading", font=("Segoe UI", 14, "bold"))
        
        # Variables para la búsqueda y autocompletado
        self._estudiantes_data: List[Tuple[int, str]] = []
        self._filtered_estudiantes: List[Tuple[int, str]] = []
        self._selected_estudiante_id: Optional[int] = None
        self.suggestions_toplevel = None
        self.suggestions_listbox = None

        self._build_header()
        self._build_layout()
        self._build_section1(self.center_frame)
        self._build_section2(self.center_frame)
        self._build_section3(self.center_frame)
        self._load_estudiantes_data()
        self._setup_search_events()

    def _build_header(self) -> None:
        """Construye el encabezado."""
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=12, pady=12)
        ttk.Label(header, text="Consultar Datos", font=("Segoe UI", 16, "bold")).pack()

    def _build_layout(self) -> None:
        """Construye el layout principal."""
        # Frame principal centrado
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Frame interno para centrar el contenido
        self.center_frame = ttk.Frame(main_frame)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

    def _build_section1(self, parent: ttk.Frame) -> None:
        """Construye la sección 1 con los 4 inputs."""
        # Frame para la sección (85% del ancho)
        section_frame = ttk.Frame(parent)
        section_frame.pack(pady=20, fill=tk.X)
        
        # Título de la sección
        title_label = ttk.Label(section_frame, text="Datos del Estudiante", font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(section_frame)
        content_frame.pack(fill=tk.X, padx=20)
        
        # Configurar el ancho del frame padre para que sea 85% del total
        parent.update_idletasks()
        parent_width = parent.winfo_width()
        if parent_width > 0:
            content_frame.configure(width=int(parent_width * 0.85))

        # Frame principal para inputs (distribución en 2 filas)
        main_inputs_frame = ttk.Frame(content_frame)
        main_inputs_frame.pack(fill=tk.X, pady=10)
        
        # Configurar columnas para distribución horizontal
        for i in range(2):
            main_inputs_frame.columnconfigure(i, weight=1)

        # Fila 1: Nombre e Institución
        # Nombre (con autocompletado)
        self.entry_nombre = ttk.Entry(main_inputs_frame, width=20, font=("Segoe UI", 14))
        self.entry_nombre.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5, ipady=8)
        
        # Agregar texto "Nombre" como contenido inicial
        self.entry_nombre.insert(0, "Nombre")

        # Institución (solo lectura)
        self.entry_institucion = ttk.Entry(main_inputs_frame, width=20, state="readonly", font=("Segoe UI", 14))
        self.entry_institucion.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=8)

        # Fila 2: Grado y Teléfono
        # Grado (solo lectura)
        self.entry_grado = ttk.Entry(main_inputs_frame, width=20, state="readonly", font=("Segoe UI", 14))
        self.entry_grado.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=5, ipady=8)

        # Teléfono (solo lectura)
        self.entry_telefono = ttk.Entry(main_inputs_frame, width=20, state="readonly", font=("Segoe UI", 14))
        self.entry_telefono.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5, ipady=8)


    def _build_section2(self, parent: ttk.Frame) -> None:
        """Construye la sección 2 con la tabla de solvencia."""
        # Frame para la sección 2 (85% del ancho)
        section2_frame = ttk.Frame(parent)
        section2_frame.pack(pady=20, fill=tk.X)
        
        # Título de la sección
        title_label = ttk.Label(section2_frame, text="Estado de Solvencia", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(section2_frame)
        content_frame.pack(fill=tk.X, padx=20)
        
        
        # Frame para la tabla
        table_frame = ttk.Frame(content_frame)
        table_frame.pack(fill=tk.X, pady=10)
        
        # Crear la tabla de solvencia (12 columnas x 2 filas)
        self._create_solvency_table(table_frame)
        
        # Frame para el estado de solvencia
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Label y cuadro de estado
        ttk.Label(status_frame, text="Estado Solvencia:", 
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.solvency_status_label = ttk.Label(status_frame, text="", 
                                              font=("Segoe UI", 14, "bold"),
                                              relief="solid", borderwidth=2,
                                              width=15, anchor="center")
        self.solvency_status_label.pack(side=tk.LEFT)

    def _create_solvency_table(self, parent: ttk.Frame) -> None:
        """Crea la tabla de solvencia con 12 columnas y 2 filas."""
        # Encabezados de la tabla
        headers = ["Inscripcion", "Enero", "Febrero", "Marzo", "Abril", "Mayo", 
                  "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre"]
        
        # Crear frame para la tabla
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.X)
        
        # Crear encabezados
        header_frame = ttk.Frame(table_container)
        header_frame.pack(fill=tk.X)
        
        self.solvency_headers = []
        for i, header in enumerate(headers):
            label = ttk.Label(header_frame, text=header, font=("Segoe UI", 12, "bold"),
                             relief="solid", borderwidth=1, width=10, anchor="center")
            label.grid(row=0, column=i, padx=1, pady=1, sticky="ew")
            self.solvency_headers.append(label)
            header_frame.columnconfigure(i, weight=1)
        
        # Crear fila de datos
        data_frame = ttk.Frame(table_container)
        data_frame.pack(fill=tk.X)
        
        self.solvency_data_labels = []
        for i in range(len(headers)):
            label = ttk.Label(data_frame, text="", font=("Segoe UI", 12),
                             relief="solid", borderwidth=1, width=10, anchor="center")
            label.grid(row=0, column=i, padx=1, pady=1, sticky="ew")
            self.solvency_data_labels.append(label)
            data_frame.columnconfigure(i, weight=1)

    def _build_section3(self, parent: ttk.Frame) -> None:
        """Construye la sección 3 con dos cuadros: Solvencia de Exámenes y Notas."""
        # Frame principal para la sección 3
        section3_frame = ttk.Frame(parent)
        section3_frame.pack(pady=20, fill=tk.X)
        
        # Título de la sección
        title_label = ttk.Label(section3_frame, text="Información Académica", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(section3_frame)
        content_frame.pack(fill=tk.X, padx=20)
        
        # Frame para los dos cuadros lado a lado
        boxes_frame = ttk.Frame(content_frame)
        boxes_frame.pack(fill=tk.X, pady=10)
        boxes_frame.columnconfigure(0, weight=1)
        boxes_frame.columnconfigure(1, weight=1)
        
        # Cuadro 1: Solvencia de Exámenes
        self._build_exam_solvency_box(boxes_frame)
        
        # Cuadro 2: Notas
        self._build_grades_box(boxes_frame)
        
        # Frame para los botones
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón Cerrar Sesión
        self.btn_cerrar_sesion = ttk.Button(buttons_frame, text="Cerrar Sesión", 
                                           command=self._on_cerrar_sesion_click, style="Logout.TButton")
        self.btn_cerrar_sesion.pack(side=tk.LEFT, padx=(0, 10), ipady=4)
        
        # Botón Salir
        self.btn_salir = ttk.Button(buttons_frame, text="Salir", 
                                   command=self._on_salir_click, style="Exit.TButton")
        self.btn_salir.pack(side=tk.LEFT, ipady=4)

    def _build_exam_solvency_box(self, parent: ttk.Frame) -> None:
        """Construye el cuadro de Solvencia de Exámenes."""
        # Frame para el cuadro de exámenes
        exam_frame = ttk.Frame(parent)
        exam_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Título del cuadro
        title_label = ttk.Label(exam_frame, text="Solvencia de Exámenes", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(exam_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Crear tabla de exámenes (2 columnas x 5 filas)
        self._create_exam_solvency_table(content_frame)

    def _build_grades_box(self, parent: ttk.Frame) -> None:
        """Construye el cuadro de Notas."""
        # Frame para el cuadro de notas
        grades_frame = ttk.Frame(parent)
        grades_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Título del cuadro
        title_label = ttk.Label(grades_frame, text="Notas", font=("Segoe UI", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 8))
        
        # Frame para el contenido
        content_frame = ttk.Frame(grades_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Crear tabla de notas (3 columnas x 5 filas)
        self._create_grades_table(content_frame)
        
        # Frame para el estado de notas
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Label y cuadro de estado
        ttk.Label(status_frame, text="Estatus:", 
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.grades_status_label = ttk.Label(status_frame, text="", 
                                            font=("Segoe UI", 14, "bold"),
                                            relief="solid", borderwidth=2,
                                            width=15, anchor="center")
        self.grades_status_label.pack(side=tk.LEFT)

    def _create_exam_solvency_table(self, parent: ttk.Frame) -> None:
        """Crea la tabla de solvencia de exámenes (2 columnas x 5 filas)."""
        # Frame para la tabla
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.X)
        
        # Configurar columnas
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=1)
        
        # Crear encabezados
        ttk.Label(table_frame, text="Concepto", font=("Segoe UI", 14, "bold"),
                 relief="solid", borderwidth=1).grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        ttk.Label(table_frame, text="Estado", font=("Segoe UI", 14, "bold"),
                 relief="solid", borderwidth=1).grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        
        # Crear filas de datos (5 filas)
        self.exam_data_labels = []
        for i in range(5):
            # Columna 1: Concepto
            concepto_label = ttk.Label(table_frame, text="", font=("Segoe UI", 14),
                                      relief="solid", borderwidth=1)
            concepto_label.grid(row=i+1, column=0, sticky="ew", padx=1, pady=1)
            
            # Columna 2: Estado
            estado_label = ttk.Label(table_frame, text="", font=("Segoe UI", 14),
                                    relief="solid", borderwidth=1)
            estado_label.grid(row=i+1, column=1, sticky="ew", padx=1, pady=1)
            
            self.exam_data_labels.append((concepto_label, estado_label))

    def _create_grades_table(self, parent: ttk.Frame) -> None:
        """Crea la tabla de notas (3 columnas x 5 filas)."""
        # Frame para la tabla
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.X)
        
        # Configurar columnas
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=1)
        table_frame.columnconfigure(2, weight=1)
        
        # Crear encabezados
        ttk.Label(table_frame, text="Nota", font=("Segoe UI", 14, "bold"),
                 relief="solid", borderwidth=1).grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        ttk.Label(table_frame, text="Calificación", font=("Segoe UI", 14, "bold"),
                 relief="solid", borderwidth=1).grid(row=0, column=1, sticky="ew", padx=1, pady=1)
        ttk.Label(table_frame, text="Estado", font=("Segoe UI", 14, "bold"),
                 relief="solid", borderwidth=1).grid(row=0, column=2, sticky="ew", padx=1, pady=1)
        
        # Crear filas de datos (4 filas + 1 fila combinada)
        self.grades_data_labels = []
        for i in range(4):
            # Columna 1: Nota
            nota_label = ttk.Label(table_frame, text=f"Nota {i+1}", font=("Segoe UI", 14),
                                  relief="solid", borderwidth=1)
            nota_label.grid(row=i+1, column=0, sticky="ew", padx=1, pady=1)
            
            # Columna 2: Calificación
            calif_label = ttk.Label(table_frame, text="", font=("Segoe UI", 14),
                                   relief="solid", borderwidth=1)
            calif_label.grid(row=i+1, column=1, sticky="ew", padx=1, pady=1)
            
            # Columna 3: Estado
            estado_label = ttk.Label(table_frame, text="", font=("Segoe UI", 14),
                                    relief="solid", borderwidth=1)
            estado_label.grid(row=i+1, column=2, sticky="ew", padx=1, pady=1)
            
            self.grades_data_labels.append((nota_label, calif_label, estado_label))
        
        # Fila 5: Promedio (combinada)
        promedio_label = ttk.Label(table_frame, text="Promedio", font=("Segoe UI", 14, "bold"),
                                  relief="solid", borderwidth=1)
        promedio_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=1, pady=1)
        
        self.promedio_value_label = ttk.Label(table_frame, text="", font=("Segoe UI", 14, "bold"),
                                             relief="solid", borderwidth=1)
        self.promedio_value_label.grid(row=5, column=2, sticky="ew", padx=1, pady=1)

    def _load_estudiantes_data(self) -> None:
        """Carga los datos de estudiantes para la búsqueda."""
        self._estudiantes_data = fetch_estudiantes_for_autocomplete("academia.db")

    def _setup_search_events(self) -> None:
        """Configura los eventos para la búsqueda y autocompletado."""
        # Eventos para el campo nombre
        self.entry_nombre.bind("<KeyRelease>", self._on_nombre_key_release)
        self.entry_nombre.bind("<KeyPress>", self._on_nombre_key_press)
        self.entry_nombre.bind("<FocusOut>", self._on_nombre_focus_out)
        self.entry_nombre.bind("<Escape>", lambda e: self._hide_suggestions())
        
        # Evento para ocultar sugerencias al hacer clic en cualquier parte de la ventana
        self.bind("<Button-1>", self._on_window_click)

    def _on_nombre_key_release(self, event: tk.Event) -> None:
        """Maneja la liberación de teclas en el campo nombre."""
        # Ignorar teclas de navegación
        if event.keysym in ["Up", "Down", "Return", "Escape"]:
            return
        
        search_text = self.entry_nombre.get().strip()
        
        if len(search_text) >= 1:
            try:
                self._filtered_estudiantes = search_estudiantes_by_name(search_text, "academia.db")
                self._show_suggestions()
            except Exception as e:
                print(f"Error en búsqueda: {e}")
                self._hide_suggestions()
        else:
            self._hide_suggestions()

    def _on_nombre_key_press(self, event: tk.Event) -> None:
        """Maneja la presión de teclas en el campo nombre."""
        # Solo manejar navegación si hay sugerencias
        if not self._filtered_estudiantes:
            return
            
        if event.keysym == "Up":
            self._navigate_suggestions(-1)
            return "break"
        elif event.keysym == "Down":
            self._navigate_suggestions(1)
            return "break"
        elif event.keysym == "Return":
            self._hide_suggestions()
            if self._filtered_estudiantes:
                self._select_current_suggestion()
            else:
                # Si no hay sugerencias, buscar directamente
                search_text = self.entry_nombre.get().strip()
                if search_text:
                    self._search_estudiante_by_name(search_text)
            return "break"
        elif event.keysym == "Escape":
            self._hide_suggestions()
            return "break"

    def _on_nombre_focus_out(self, event: tk.Event) -> None:
        """Maneja la pérdida de foco del campo nombre."""
        # Pequeño delay para permitir que el click en el listbox funcione
        self.after(150, self._hide_suggestions)
    
    def _on_window_click(self, event: tk.Event) -> None:
        """Maneja clics en la ventana para ocultar sugerencias."""
        # Verificar si el clic fue fuera del campo nombre y del listbox
        widget = event.widget
        if widget != self.entry_nombre and (self.suggestions_listbox is None or widget != self.suggestions_listbox):
            self._hide_suggestions()

    def _hide_suggestions(self) -> None:
        """Oculta las sugerencias del listbox."""
        if self.suggestions_toplevel is not None:
            # Limpiar el contenido del listbox
            if self.suggestions_listbox is not None:
                self.suggestions_listbox.delete(0, tk.END)
            # Ocultar el Toplevel
            self.suggestions_toplevel.withdraw()

    def _show_suggestions(self) -> None:
        """Muestra las sugerencias en el listbox (estilo Google)."""
        if not self._filtered_estudiantes:
            self._hide_suggestions()
            return
            
        # Limitar a 5 sugerencias máximo (como Google)
        suggestions = self._filtered_estudiantes[:5]
        
        # Crear el Toplevel si no existe
        if self.suggestions_toplevel is None:
            self._create_suggestions_toplevel()
        
        # Limpiar y llenar el listbox
        self.suggestions_listbox.delete(0, tk.END)
        for _, nombre in suggestions:
            self.suggestions_listbox.insert(tk.END, nombre)
        
        # Posicionar el Toplevel debajo del campo nombre
        self._position_suggestions_overlay()
    
    def _position_suggestions_overlay(self) -> None:
        """Posiciona el Toplevel de sugerencias debajo del campo nombre."""
        if self.suggestions_toplevel is None:
            return
            
        # Obtener la posición del campo nombre en coordenadas de pantalla
        self.entry_nombre.update_idletasks()
        x = self.entry_nombre.winfo_rootx()
        y = self.entry_nombre.winfo_rooty() + self.entry_nombre.winfo_height()
        width = self.entry_nombre.winfo_width()
        
        # Posicionar el Toplevel
        self.suggestions_toplevel.geometry(f"{width}x{90}+{x}+{y}")
        self.suggestions_toplevel.deiconify()
        self.suggestions_toplevel.lift()
    
    def _create_suggestions_toplevel(self) -> None:
        """Crea el Toplevel para las sugerencias."""
        self.suggestions_toplevel = tk.Toplevel(self)
        self.suggestions_toplevel.withdraw()  # Inicialmente oculto
        self.suggestions_toplevel.overrideredirect(True)  # Sin bordes de ventana
        self.suggestions_toplevel.configure(bg="white")
        
        # Listbox para sugerencias
        self.suggestions_listbox = tk.Listbox(self.suggestions_toplevel, 
                                            height=3, 
                                            relief="solid", 
                                            borderwidth=1,
                                            font=("Segoe UI", 12),
                                            selectbackground="#4285f4",
                                            selectforeground="white",
                                            bg="white",
                                            highlightthickness=0,
                                            activestyle="none")
        self.suggestions_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Eventos para el listbox
        self.suggestions_listbox.bind("<Double-Button-1>", self._on_suggestion_select)
        self.suggestions_listbox.bind("<Button-1>", self._on_suggestion_select)

    def _navigate_suggestions(self, direction: int) -> None:
        """Navega por las sugerencias con las flechas (estilo Google)."""
        if not self._filtered_estudiantes:
            return
            
        current_selection = self.suggestions_listbox.curselection()
        if not current_selection:
            # Si no hay selección, seleccionar el primero
            self.suggestions_listbox.selection_set(0)
        else:
            current_index = current_selection[0]
            new_index = current_index + direction
            
            # Limitar el rango (como Google)
            max_index = min(len(self._filtered_estudiantes) - 1, 4)  # Máximo 5 elementos
            if new_index < 0:
                new_index = 0  # No circular, quedarse en el primero
            elif new_index > max_index:
                new_index = max_index  # No circular, quedarse en el último
                
            self.suggestions_listbox.selection_clear(0, tk.END)
            self.suggestions_listbox.selection_set(new_index)
            self.suggestions_listbox.see(new_index)

    def _select_current_suggestion(self) -> None:
        """Selecciona la sugerencia actual."""
        if not self._filtered_estudiantes:
            return
            
        selection = self.suggestions_listbox.curselection()
        if not selection:
            # Si no hay selección, seleccionar el primero
            self.suggestions_listbox.selection_set(0)
            selection = (0,)
            
        index = selection[0]
        if index < len(self._filtered_estudiantes):
            estudiante_id, nombre_completo = self._filtered_estudiantes[index]
            
            # Actualizar el campo nombre
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, nombre_completo)
            
            # Ocultar sugerencias
            self._hide_suggestions()
            
            # Buscar y mostrar los datos del estudiante
            self._load_estudiante_data(estudiante_id)

    def _on_suggestion_select(self, event: tk.Event) -> None:
        """Maneja la selección de una sugerencia."""
        selection = self.suggestions_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self._filtered_estudiantes):
            estudiante_id, nombre_completo = self._filtered_estudiantes[index]
            
            # Actualizar el campo nombre
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, nombre_completo)
            
            # Ocultar sugerencias
            self._hide_suggestions()
            
            # Buscar y mostrar los datos del estudiante
            self._load_estudiante_data(estudiante_id)





    def _load_estudiante_data(self, estudiante_id: int) -> None:
        """Carga y muestra los datos del estudiante seleccionado."""
        data = fetch_estudiante_complete_data(estudiante_id, "academia.db")
        if data:
            nombre_completo, grado, telefono, institucion = data
            
            # Limpiar campos
            self._clear_readonly_fields()
            
            # Llenar campos (usando el método interno para campos readonly)
            self._set_readonly_field(self.entry_grado, grado)
            self._set_readonly_field(self.entry_telefono, telefono)
            self._set_readonly_field(self.entry_institucion, institucion)
            
            self._selected_estudiante_id = estudiante_id
            
            # Actualizar tabla de solvencia
            self._update_solvency_table(estudiante_id)
            
            # Actualizar estado de solvencia
            self._update_solvency_status(estudiante_id)
            
            # Actualizar tabla de exámenes
            self._update_exam_solvency_table(estudiante_id)
            
            # Actualizar tabla de notas
            self._update_grades_table(estudiante_id)
            
            # Actualizar estado de notas
            self._update_grades_status(estudiante_id)

    def _clear_readonly_fields(self) -> None:
        """Limpia los campos de solo lectura."""
        self._set_readonly_field(self.entry_grado, "")
        self._set_readonly_field(self.entry_telefono, "")
        self._set_readonly_field(self.entry_institucion, "")

    def _set_readonly_field(self, entry: ttk.Entry, value: str) -> None:
        """Establece el valor de un campo de solo lectura."""
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.config(state="readonly")

    def _update_solvency_table(self, estudiante_id: int) -> None:
        """Actualiza la tabla de solvencia con los datos del estudiante."""
        # Limpiar la tabla
        for label in self.solvency_data_labels:
            label.config(text="")
        
        # Obtener conceptos de pago
        conceptos = fetch_conceptos_pago_for_solvency("academia.db")
        
        # Mapeo de conceptos a columnas (asumiendo orden secuencial)
        for i, (concepto_id, concepto_nombre) in enumerate(conceptos):
            if i < len(self.solvency_data_labels):
                # Obtener pagos para este concepto
                pagos = fetch_pagos_by_estudiante_and_concepto(estudiante_id, concepto_id, "academia.db")
                
                if pagos:
                    # Mostrar el monto total pagado
                    total = sum(pagos)
                    self.solvency_data_labels[i].config(text=f"Q{total:.2f}")
                else:
                    self.solvency_data_labels[i].config(text="No pagado")

    def _update_solvency_status(self, estudiante_id: int) -> None:
        """Actualiza el estado de solvencia del estudiante."""
        is_solvent, status_text = check_solvency_status(estudiante_id, "academia.db")
        
        self.solvency_status_label.config(text=status_text)
        
        # Configurar colores
        if is_solvent:
            self.solvency_status_label.config(foreground="green", background="lightgreen")
        else:
            self.solvency_status_label.config(foreground="red", background="lightcoral")

    def _update_exam_solvency_table(self, estudiante_id: int) -> None:
        """Actualiza la tabla de solvencia de exámenes."""
        # Limpiar la tabla
        for concepto_label, estado_label in self.exam_data_labels:
            concepto_label.config(text="")
            estado_label.config(text="")
        
        # Obtener conceptos de exámenes
        conceptos = fetch_exam_conceptos_pago("academia.db")
        
        # Llenar la tabla
        for i, (concepto_id, concepto_nombre) in enumerate(conceptos):
            if i < len(self.exam_data_labels):
                concepto_label, estado_label = self.exam_data_labels[i]
                
                # Mostrar el nombre del concepto
                concepto_label.config(text=concepto_nombre)
                
                # Verificar si hay pagos
                pagos = fetch_pagos_by_estudiante_and_concepto(estudiante_id, concepto_id, "academia.db")
                
                if pagos:
                    # Mostrar el monto total pagado
                    total = sum(pagos)
                    estado_label.config(text=f"Q{total:.2f}")
                else:
                    estado_label.config(text="0")

    def _update_grades_table(self, estudiante_id: int) -> None:
        """Actualiza la tabla de notas."""
        # Limpiar la tabla
        for nota_label, calif_label, estado_label in self.grades_data_labels:
            calif_label.config(text="")
            estado_label.config(text="")
        self.promedio_value_label.config(text="")
        
        # Obtener calificaciones del estudiante
        calificaciones = fetch_calificaciones_by_estudiante(estudiante_id, "academia.db")
        
        if calificaciones:
            nota_uno, nota_dos, nota_tres, nota_cuatro = calificaciones
            notas = [nota_uno, nota_dos, nota_tres, nota_cuatro]
            
            # Llenar la tabla
            for i, nota in enumerate(notas):
                if i < len(self.grades_data_labels):
                    _, calif_label, estado_label = self.grades_data_labels[i]
                    
                    # Mostrar la calificación
                    calif_label.config(text=f"{nota:.1f}")
                    
                    # Mostrar el estado (aprobado/reprobado)
                    if is_approved(nota):
                        estado_label.config(text="Aprobado", foreground="green")
                    else:
                        estado_label.config(text="Reprobado", foreground="red")
            
            # Calcular y mostrar el promedio
            promedio = calculate_average(calificaciones)
            self.promedio_value_label.config(text=f"{promedio:.1f}")

    def _update_grades_status(self, estudiante_id: int) -> None:
        """Actualiza el estado general de las notas."""
        calificaciones = fetch_calificaciones_by_estudiante(estudiante_id, "academia.db")
        
        if calificaciones:
            promedio = calculate_average(calificaciones)
            
            if is_approved(promedio):
                self.grades_status_label.config(text="Aprobado", 
                                               foreground="green", background="lightgreen")
            else:
                self.grades_status_label.config(text="Reprobado", 
                                               foreground="red", background="lightcoral")
        else:
            self.grades_status_label.config(text="Sin datos", 
                                           foreground="gray", background="lightgray")

    def _on_buscar_click(self) -> None:
        """Maneja el click del botón Buscar."""
        search_text = self.entry_nombre.get().strip()
        if search_text:
            # Buscar el estudiante por nombre
            self._search_estudiante_by_name(search_text)
        else:
            # Limpiar todos los campos si no hay texto
            self._clear_all_fields()

    def _on_cerrar_sesion_click(self) -> None:
        """Maneja el click del botón Cerrar Sesión."""
        # Usar el callback de logout si está disponible
        if self.on_logout_callback:
            self.on_logout_callback()
        else:
            # Fallback: buscar la ventana principal para hacer logout
            if hasattr(self, 'master') and hasattr(self.master, 'master'):
                # Si tenemos acceso a la ventana principal
                main_window = self.master.master
                if hasattr(main_window, 'logout'):
                    main_window.logout()
                else:
                    # Si no hay método logout, cerrar la ventana actual
                    self.master.destroy()
            else:
                # Fallback: cerrar la ventana actual
                self.master.destroy()

    def _on_salir_click(self) -> None:
        """Maneja el click del botón Salir."""
        # Cerrar toda la aplicación
        if hasattr(self, 'master') and hasattr(self.master, 'master'):
            main_window = self.master.master
            main_window.destroy()
        else:
            self.master.destroy()

    def _clear_all_fields(self) -> None:
        """Limpia todos los campos del formulario."""
        self.entry_nombre.delete(0, tk.END)
        self.entry_grado.config(state="normal")
        self.entry_grado.delete(0, tk.END)
        self.entry_grado.config(state="readonly")
        self.entry_telefono.config(state="normal")
        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.config(state="readonly")
        self.entry_institucion.config(state="normal")
        self.entry_institucion.delete(0, tk.END)
        self.entry_institucion.config(state="readonly")
        
        # Limpiar las tablas
        self._clear_solvency_table()
        self._clear_exam_solvency_table()
        self._clear_grades_table()
        
        # Limpiar estados
        self.solvency_status_label.config(text="", foreground="black", background="white")
        self.grades_status_label.config(text="", foreground="black", background="white")

    def _clear_solvency_table(self) -> None:
        """Limpia la tabla de solvencia."""
        if hasattr(self, 'solvency_data_labels'):
            for _, monto_label in self.solvency_data_labels:
                monto_label.config(text="0")

    def _clear_exam_solvency_table(self) -> None:
        """Limpia la tabla de solvencia de exámenes."""
        if hasattr(self, 'exam_solvency_data_labels'):
            for _, monto_label in self.exam_solvency_data_labels:
                monto_label.config(text="0")

    def _clear_grades_table(self) -> None:
        """Limpia la tabla de notas."""
        if hasattr(self, 'grades_data_labels'):
            for _, calif_label, estado_label in self.grades_data_labels:
                calif_label.config(text="")
                estado_label.config(text="")
        if hasattr(self, 'promedio_value_label'):
            self.promedio_value_label.config(text="")

    def _search_estudiante_by_name(self, search_text: str) -> None:
        """Busca un estudiante por nombre y carga sus datos."""
        try:
            # Buscar estudiantes que coincidan con el texto
            resultados = search_estudiantes_by_name(search_text, "academia.db")
            
            if resultados:
                # Si hay resultados, tomar el primero
                estudiante_id, nombre_completo = resultados[0]
                
                # Cargar los datos del estudiante
                datos = fetch_estudiante_complete_data(estudiante_id, "academia.db")
                
                if datos:
                    nombre, grado, telefono, institucion = datos
                    
                    # Actualizar los campos
                    self.entry_nombre.delete(0, tk.END)
                    self.entry_nombre.insert(0, nombre)
                    
                    self.entry_grado.config(state="normal")
                    self.entry_grado.delete(0, tk.END)
                    self.entry_grado.insert(0, grado)
                    self.entry_grado.config(state="readonly")
                    
                    self.entry_telefono.config(state="normal")
                    self.entry_telefono.delete(0, tk.END)
                    self.entry_telefono.insert(0, telefono)
                    self.entry_telefono.config(state="readonly")
                    
                    self.entry_institucion.config(state="normal")
                    self.entry_institucion.delete(0, tk.END)
                    self.entry_institucion.insert(0, institucion)
                    self.entry_institucion.config(state="readonly")
                    
                    # Actualizar las secciones 2 y 3
                    self._update_solvency_table(estudiante_id)
                    self._update_solvency_status(estudiante_id)
                    self._update_exam_solvency_table(estudiante_id)
                    self._update_grades_table(estudiante_id)
                    self._update_grades_status(estudiante_id)
                    
                    print(f"DEBUG: Estudiante encontrado: {nombre}")
                else:
                    print(f"DEBUG: No se encontraron datos para el estudiante ID: {estudiante_id}")
            else:
                print(f"DEBUG: No se encontraron estudiantes con el nombre: {search_text}")
                # Limpiar campos si no se encuentra nada
                self._clear_all_fields()
                
        except Exception as e:
            print(f"DEBUG: Error al buscar estudiante: {e}")
            self._clear_all_fields()
