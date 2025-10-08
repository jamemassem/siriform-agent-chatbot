"""Field validation tool for checking values against JSON Schema."""
from typing import Any, Dict, Tuple
import re
from datetime import datetime


async def validate_field(
    field_name: str,
    value: Any,
    form_schema: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Validate a field value against the form's JSON Schema.
    
    Checks:
    - Required fields (must be present and non-empty)
    - Type constraints (string, integer, array, etc.)
    - Pattern matching (regex for phone numbers, emails, etc.)
    - Enum values (value must be in allowed list)
    - Number ranges (minimum, maximum)
    - String length (minLength, maxLength)
    - Array constraints (minItems, maxItems)
    - Date/time formats
    
    Args:
        field_name: Name of the field to validate
        value: Value to validate
        form_schema: JSON Schema of the form
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid: (True, "")
        If invalid: (False, "Error description")
    """
    properties = form_schema.get('properties', {})
    required_fields = form_schema.get('required', [])
    
    # Check if field exists in schema
    if field_name not in properties:
        return False, f"Field '{field_name}' not found in form schema"
    
    field_def = properties[field_name]
    field_type = field_def.get('type')
    
    # Check required fields
    if field_name in required_fields:
        if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
            return False, f"Field '{field_name}' is required"
    
    # Allow None/empty for optional fields
    if value is None or value == "":
        if field_name not in required_fields:
            return True, ""
    
    # Type validation
    type_checks = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'boolean': bool,
        'array': list,
        'object': dict
    }
    
    if field_type in type_checks:
        expected_type = type_checks[field_type]
        if not isinstance(value, expected_type):
            return False, f"Field '{field_name}' must be of type {field_type}, got {type(value).__name__}"
    
    # String validations
    if field_type == 'string' and isinstance(value, str):
        # Pattern validation
        if 'pattern' in field_def:
            pattern = field_def['pattern']
            if not re.match(pattern, value):
                return False, f"Field '{field_name}' does not match required pattern: {pattern}"
        
        # Length validation
        if 'minLength' in field_def:
            if len(value) < field_def['minLength']:
                return False, f"Field '{field_name}' must be at least {field_def['minLength']} characters"
        
        if 'maxLength' in field_def:
            if len(value) > field_def['maxLength']:
                return False, f"Field '{field_name}' must be at most {field_def['maxLength']} characters"
        
        # Format validation
        if 'format' in field_def:
            format_type = field_def['format']
            if format_type == 'date':
                try:
                    datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    return False, f"Field '{field_name}' must be a valid date (YYYY-MM-DD)"
            elif format_type == 'time':
                try:
                    datetime.strptime(value, '%H:%M')
                except ValueError:
                    return False, f"Field '{field_name}' must be a valid time (HH:MM)"
            elif format_type == 'date-time':
                try:
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return False, f"Field '{field_name}' must be a valid ISO 8601 datetime"
            elif format_type == 'email':
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    return False, f"Field '{field_name}' must be a valid email address"
    
    # Integer/Number validations
    if field_type in ['integer', 'number'] and isinstance(value, (int, float)):
        if 'minimum' in field_def:
            if value < field_def['minimum']:
                return False, f"Field '{field_name}' must be at least {field_def['minimum']}"
        
        if 'maximum' in field_def:
            if value > field_def['maximum']:
                return False, f"Field '{field_name}' must be at most {field_def['maximum']}"
        
        if 'exclusiveMinimum' in field_def:
            if value <= field_def['exclusiveMinimum']:
                return False, f"Field '{field_name}' must be greater than {field_def['exclusiveMinimum']}"
        
        if 'exclusiveMaximum' in field_def:
            if value >= field_def['exclusiveMaximum']:
                return False, f"Field '{field_name}' must be less than {field_def['exclusiveMaximum']}"
    
    # Enum validation
    if 'enum' in field_def:
        if value not in field_def['enum']:
            return False, f"Field '{field_name}' must be one of: {', '.join(map(str, field_def['enum']))}"
    
    # Array validations
    if field_type == 'array' and isinstance(value, list):
        if 'minItems' in field_def:
            if len(value) < field_def['minItems']:
                return False, f"Field '{field_name}' must have at least {field_def['minItems']} items"
        
        if 'maxItems' in field_def:
            if len(value) > field_def['maxItems']:
                return False, f"Field '{field_name}' must have at most {field_def['maxItems']} items"
        
        # Validate array items if schema is provided
        if 'items' in field_def:
            items_schema = field_def['items']
            for i, item in enumerate(value):
                # For object items, validate each property
                if items_schema.get('type') == 'object' and isinstance(item, dict):
                    item_properties = items_schema.get('properties', {})
                    item_required = items_schema.get('required', [])
                    
                    for prop_name, prop_value in item.items():
                        if prop_name in item_properties:
                            # Recursively validate nested field
                            # Create a mini-schema for this property
                            mini_schema = {
                                'properties': {prop_name: item_properties[prop_name]},
                                'required': [prop_name] if prop_name in item_required else []
                            }
                            is_valid, error = await validate_field(prop_name, prop_value, mini_schema)
                            if not is_valid:
                                return False, f"Array item {i}: {error}"
    
    return True, ""
