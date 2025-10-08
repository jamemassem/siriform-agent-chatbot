"""Natural language request analyzer tool."""
from typing import Any, Dict, List, Optional
import re
from datetime import datetime


async def analyze_user_request(
    user_message: str,
    form_schema: Dict[str, Any],
    llm_client: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Analyze user's natural language request and extract structured information.
    
    This function uses pattern matching and optional LLM analysis to extract:
    - Quantities (e.g., "2 laptops")
    - Dates and times (e.g., "tomorrow", "next Monday")
    - Locations (e.g., "Building A", "ตึกศรีจันทร์")
    - Equipment types
    - Other form-relevant data
    
    Args:
        user_message: User's natural language input
        form_schema: JSON Schema of the form to extract data for
        llm_client: Optional LLM client for advanced analysis
        
    Returns:
        Dictionary containing:
        - extracted_data: Dict of field names to extracted values
        - confidence: Float between 0.0 and 1.0
        - ambiguities: List of fields that need clarification
    """
    extracted_data = {}
    ambiguities = []
    confidence_scores = []
    
    # Extract quantities using regex
    quantity_pattern = r'(\d+)\s*(laptop|notebook|desktop|monitor|เครื่อง|คอมพิวเตอร์)'
    quantity_matches = re.findall(quantity_pattern, user_message.lower())
    
    if quantity_matches:
        # Extract equipment information
        equipments = []
        for qty, equip_type in quantity_matches:
            # Map Thai terms to English
            type_mapping = {
                'laptop': 'Notebook',
                'notebook': 'Notebook',
                'desktop': 'Desktop',
                'monitor': 'Monitor',
                'เครื่อง': 'Notebook',  # Generic, default to notebook
                'คอมพิวเตอร์': 'Desktop'
            }
            equipment_type = type_mapping.get(equip_type.lower(), 'Notebook')
            equipments.append({
                'type': equipment_type,
                'quantity': int(qty),
                'detail': ''
            })
            confidence_scores.append(0.9)  # High confidence for explicit quantities
        
        extracted_data['equipments'] = equipments
    else:
        ambiguities.append('equipments')
        confidence_scores.append(0.3)
    
    # Extract dates
    date_keywords = {
        'tomorrow': 1,
        'พรุ่งนี้': 1,
        'next week': 7,
        'สัปดาห์หนา': 7,
        'today': 0,
        'วันนี้': 0
    }
    
    for keyword, days_offset in date_keywords.items():
        if keyword in user_message.lower():
            # Calculate the date
            from datetime import timedelta
            target_date = datetime.now() + timedelta(days=days_offset)
            extracted_data['requestDate'] = target_date.strftime('%Y-%m-%d')
            confidence_scores.append(0.85)
            break
    else:
        # Check for explicit date patterns (YYYY-MM-DD or DD/MM/YYYY)
        date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})'
        date_match = re.search(date_pattern, user_message)
        if date_match:
            date_str = date_match.group(1)
            if '/' in date_str:
                # Convert DD/MM/YYYY to YYYY-MM-DD
                day, month, year = date_str.split('/')
                extracted_data['requestDate'] = f"{year}-{month}-{day}"
            else:
                extracted_data['requestDate'] = date_str
            confidence_scores.append(0.95)
        else:
            ambiguities.append('requestDate')
            confidence_scores.append(0.2)
    
    # Extract time
    time_keywords = {
        'morning': '09:00',
        'เช้า': '09:00',
        'afternoon': '13:00',
        'บ่าย': '13:00',
        'evening': '17:00',
        'เย็น': '17:00'
    }
    
    for keyword, time_value in time_keywords.items():
        if keyword in user_message.lower():
            extracted_data['requestTime'] = time_value
            confidence_scores.append(0.8)
            break
    else:
        # Check for explicit time patterns (HH:MM)
        time_pattern = r'(\d{1,2}):(\d{2})'
        time_match = re.search(time_pattern, user_message)
        if time_match:
            hour, minute = time_match.groups()
            extracted_data['requestTime'] = f"{int(hour):02d}:{minute}"
            confidence_scores.append(0.95)
        else:
            ambiguities.append('requestTime')
            confidence_scores.append(0.2)
    
    # Extract location (building)
    building_pattern = r'(building|ตึก|อาคาร)\s*([A-Z]|\w+)'
    building_match = re.search(building_pattern, user_message, re.IGNORECASE)
    if building_match:
        extracted_data['deliveryLocation'] = user_message[building_match.start():building_match.end()]
        confidence_scores.append(0.85)
    else:
        ambiguities.append('deliveryLocation')
        confidence_scores.append(0.3)
    
    # Calculate overall confidence
    overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    return {
        'extracted_data': extracted_data,
        'confidence': round(overall_confidence, 2),
        'ambiguities': ambiguities
    }
