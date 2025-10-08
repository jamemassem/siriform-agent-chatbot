"""Fuzzy matching tool for looking up information in form schema."""
from typing import Any, Dict, List, Tuple
from difflib import SequenceMatcher


def fuzzy_match(query: str, target: str, threshold: float = 0.6) -> float:
    """
    Calculate similarity ratio between query and target strings.
    
    Args:
        query: Search query
        target: String to compare against
        threshold: Minimum similarity ratio (0.0 to 1.0)
        
    Returns:
        Similarity ratio between 0.0 and 1.0
    """
    # Normalize strings for comparison
    query_normalized = query.lower().strip()
    target_normalized = target.lower().strip()
    
    # Calculate similarity
    ratio = SequenceMatcher(None, query_normalized, target_normalized).ratio()
    
    return ratio


async def lookup_information(
    query: str,
    form_schema: Dict[str, Any],
    field_name: str,
    threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Perform fuzzy matching to find valid options for a field in the form schema.
    
    This tool helps when users provide partial or misspelled information.
    For example:
    - "ตึกศรี" matches "ตึกศรีจันทร์" (Building Srichand)
    - "note" matches "Notebook"
    - "comp sci" matches "Computer Science"
    
    Args:
        query: User's search query (can be partial or Thai/English)
        form_schema: JSON Schema of the form
        field_name: Name of the field to search in
        threshold: Minimum similarity score (0.0 to 1.0, default 0.6)
        
    Returns:
        List of matching options, sorted by confidence score (highest first)
        Each option is a dict with:
        - value: The matched value
        - confidence: Similarity score (0.0 to 1.0)
        - label: Display label if available
    """
    results = []
    
    # Get the field definition from schema
    properties = form_schema.get('properties', {})
    field_def = properties.get(field_name, {})
    
    # Handle enum fields
    if 'enum' in field_def:
        enum_values = field_def['enum']
        for value in enum_values:
            confidence = fuzzy_match(query, str(value), threshold)
            if confidence >= threshold:
                results.append({
                    'value': value,
                    'confidence': round(confidence, 2),
                    'label': value
                })
    
    # Handle array fields with items.enum
    elif field_def.get('type') == 'array':
        items_def = field_def.get('items', {})
        if 'properties' in items_def:
            # Array of objects - check nested enums
            for prop_name, prop_def in items_def['properties'].items():
                if 'enum' in prop_def:
                    for value in prop_def['enum']:
                        confidence = fuzzy_match(query, str(value), threshold)
                        if confidence >= threshold:
                            results.append({
                                'value': value,
                                'confidence': round(confidence, 2),
                                'label': value
                            })
    
    # Handle oneOf/anyOf patterns
    elif 'oneOf' in field_def:
        for option in field_def['oneOf']:
            if 'const' in option:
                value = option['const']
                label = option.get('title', value)
                confidence = fuzzy_match(query, str(label), threshold)
                if confidence >= threshold:
                    results.append({
                        'value': value,
                        'confidence': round(confidence, 2),
                        'label': label
                    })
    
    # Sort by confidence (highest first)
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return results
