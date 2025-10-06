"""
Configuración de tamaños y estilos para el sistema de gestión académica.

Este archivo centraliza la configuración de tamaños de fuente, padding y otros
elementos visuales para facilitar el ajuste de la interfaz según las necesidades.
"""

# Configuración de tamaños de fuente
FONT_SIZES = {
    'title': 16,           # Títulos principales
    'subtitle': 12,        # Subtítulos
    'normal': 9,           # Texto normal
    'small': 8,            # Texto pequeño
    'button': 9,           # Botones
    'entry': 9,            # Campos de entrada
    'table': 9,            # Tablas
    'table_header': 9,     # Encabezados de tabla
}

# Configuración de padding y espaciado
PADDING = {
    'small': 4,            # Padding pequeño
    'normal': 6,           # Padding normal
    'large': 8,            # Padding grande
    'button': 4,           # Padding de botones
    'entry': 4,            # Padding de campos
}

# Configuración de anchos
WIDTHS = {
    'entry_small': 15,     # Campo pequeño
    'entry_normal': 20,    # Campo normal
    'entry_large': 25,     # Campo grande
    'button_small': 10,    # Botón pequeño
    'button_normal': 12,   # Botón normal
    'button_large': 15,    # Botón grande
}

# Configuración de alturas
HEIGHTS = {
    'button': 4,           # Altura de botones (ipady)
    'entry': 4,            # Altura de campos (ipady)
    'table_row': 25,       # Altura de filas de tabla
}

# Configuración de colores
COLORS = {
    'background': '#333',
    'secondary': '#555',
    'entry': '#444',
    'text': 'white',
    'success': '#4caf50',
    'error': '#d32f2f',
    'warning': '#ff9800',
    'info': '#607d8b',
    'exit': '#9e9e9e',
}

def get_font(size_key='normal', bold=False):
    """
    Obtiene la configuración de fuente según la clave.
    
    Args:
        size_key: Clave del tamaño de fuente
        bold: Si la fuente debe ser negrita
        
    Returns:
        tuple: Configuración de fuente (family, size, weight)
    """
    size = FONT_SIZES.get(size_key, FONT_SIZES['normal'])
    weight = 'bold' if bold else 'normal'
    return ('Segoe UI', size, weight)

def get_padding(size_key='normal'):
    """
    Obtiene el padding según la clave.
    
    Args:
        size_key: Clave del tamaño de padding
        
    Returns:
        int: Valor del padding
    """
    return PADDING.get(size_key, PADDING['normal'])

def get_width(size_key='normal'):
    """
    Obtiene el ancho según la clave.
    
    Args:
        size_key: Clave del tamaño de ancho
        
    Returns:
        int: Valor del ancho
    """
    return WIDTHS.get(size_key, WIDTHS['entry_normal'])

def get_height(size_key='normal'):
    """
    Obtiene la altura según la clave.
    
    Args:
        size_key: Clave del tamaño de altura
        
    Returns:
        int: Valor de la altura
    """
    return HEIGHTS.get(size_key, HEIGHTS['button'])

def get_color(color_key):
    """
    Obtiene el color según la clave.
    
    Args:
        color_key: Clave del color
        
    Returns:
        str: Valor del color en hexadecimal
    """
    return COLORS.get(color_key, COLORS['text'])
