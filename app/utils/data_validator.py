"""
Utilidades de validación de datos centralizadas
Evita errores NoneType y duplicación de lógica
"""

class DataValidator:
    """Clase centralizada para validación segura de datos"""
    
    @staticmethod
    def safe_str(value, default=''):
        """
        Convierte cualquier valor a string de forma segura
        Maneja None, null, undefined, etc.
        """
        if value is None:
            return default
        try:
            return str(value).strip() if str(value).strip() != '' else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value, default=0):
        """
        Convierte cualquier valor a entero de forma segura
        """
        if value is None:
            return default
        try:
            return int(value) if value != '' else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float(value, default=0.0):
        """
        Convierte cualquier valor a float de forma segura
        """
        if value is None:
            return default
        try:
            return float(value) if value != '' else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_bool(value, default=False):
        """
        Convierte cualquier valor a booleano de forma segura
        """
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        try:
            return bool(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Valida que todos los campos requeridos estén presentes y no vacíos
        Returns: (is_valid, missing_fields)
        """
        missing = []
        for field in required_fields:
            if field not in data or not DataValidator.safe_str(data[field]):
                missing.append(field)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def sanitize_field(data, field_name, default=''):
        """
        Sanitiza un campo específico de forma segura
        """
        return DataValidator.safe_str(data.get(field_name, default), default)
