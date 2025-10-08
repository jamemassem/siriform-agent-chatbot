"""Form data update tool for modifying form state."""
from typing import Any, Dict, Optional
from copy import deepcopy


async def update_form_data(
    current_form_data: Dict[str, Any],
    field_path: str,
    new_value: Any,
    form_schema: Dict[str, Any],
    validate: bool = True
) -> Dict[str, Any]:
    """
    Update a field in the form data with validation.
    
    This function:
    1. Validates the new value against the form schema (if validate=True)
    2. Updates the field in the form data (supporting nested paths)
    3. Preserves existing data that isn't being updated
    4. Returns the updated form data
    
    Args:
        current_form_data: Current state of the form data
        field_path: Path to the field (e.g., "fullName" or "equipments[0].type")
        new_value: New value to set
        form_schema: JSON Schema of the form for validation
        validate: Whether to validate against schema (default: True)
        
    Returns:
        Updated form data dictionary
        
    Raises:
        ValueError: If validation fails or field path is invalid
    """
    # Import validation function
    from .validator import validate_field
    
    # Deep copy to avoid mutating original
    updated_data = deepcopy(current_form_data)
    
    # Validate the new value if requested
    if validate:
        is_valid, error_message = await validate_field(
            field_name=field_path.split('[')[0],  # Get base field name
            value=new_value,
            form_schema=form_schema
        )
        if not is_valid:
            raise ValueError(f"Validation failed for {field_path}: {error_message}")
    
    # Parse field path (support both simple and array notation)
    # Examples: "fullName", "equipments[0].type", "equipments[1].quantity"
    parts = field_path.replace('[', '.').replace(']', '').split('.')
    
    # Navigate to the target field
    current = updated_data
    for i, part in enumerate(parts[:-1]):
        # Check if part is an array index
        if part.isdigit():
            index = int(part)
            if not isinstance(current, list):
                raise ValueError(f"Expected array at path segment {i}, got {type(current)}")
            if index >= len(current):
                raise ValueError(f"Array index {index} out of range (length: {len(current)})")
            current = current[index]
        else:
            # Dictionary key
            if part not in current:
                # Initialize nested structure if it doesn't exist
                # Look ahead to see if next part is a digit (array) or string (object)
                if i + 1 < len(parts) - 1 and parts[i + 1].isdigit():
                    current[part] = []
                else:
                    current[part] = {}
            current = current[part]
    
    # Set the final value
    final_key = parts[-1]
    if final_key.isdigit():
        index = int(final_key)
        if not isinstance(current, list):
            raise ValueError(f"Expected array for final path segment, got {type(current)}")
        if index >= len(current):
            raise ValueError(f"Array index {index} out of range (length: {len(current)})")
        current[index] = new_value
    else:
        current[final_key] = new_value
    
    return updated_data
