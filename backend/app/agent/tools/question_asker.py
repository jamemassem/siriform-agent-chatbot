"""Clarifying question generator tool."""
from typing import Any, Dict, List, Optional


async def ask_clarifying_question(
    ambiguous_fields: List[str],
    form_schema: Dict[str, Any],
    context: Dict[str, Any],
    language: str = "th"
) -> str:
    """
    Generate a clarifying question to resolve ambiguities.
    
    This function generates natural, conversational questions in Thai or English
    to help gather missing or unclear information. It maintains a friendly,
    helpful persona while being concise.
    
    Args:
        ambiguous_fields: List of field names that need clarification
        form_schema: JSON Schema of the form
        context: Current conversation context including:
            - extracted_data: Data already extracted
            - confidence: Current confidence score
            - user_message: Original user message
        language: Language for the question ("th" for Thai, "en" for English)
        
    Returns:
        A clarifying question string in the specified language
    """
    properties = form_schema.get('properties', {})
    
    # If no ambiguous fields, return empty
    if not ambiguous_fields:
        return ""
    
    # Get the first ambiguous field to ask about
    field_name = ambiguous_fields[0]
    field_def = properties.get(field_name, {})
    
    # Get field label (use title if available, otherwise field name)
    field_label = field_def.get('title', field_name)
    
    # Thai question templates
    th_templates = {
        'equipments': 'คุณต้องการอุปกรณ์ประเภทใดบ้างครับ/ค่ะ? (เช่น Notebook, Desktop, Monitor)',
        'requestDate': 'คุณต้องการใช้อุปกรณ์วันที่เท่าไหร่ครับ/ค่ะ?',
        'requestTime': 'คุณต้องการรับอุปกรณ์เวลาประมาณกี่โมงครับ/ค่ะ?',
        'deliveryLocation': 'คุณต้องการให้ส่งอุปกรณ์ไปที่ไหนครับ/ค่ะ? (เช่น ตึกศรีจันทร์, อาคาร A)',
        'department': 'คุณสังกัดแผนกใดครับ/ค่ะ?',
        'position': 'คุณดำรงตำแหน่งอะไรครับ/ค่ะ?',
        'phoneNumber': 'ขอเบอร์โทรศัพท์ติดต่อของคุณหน่อยครับ/ค่ะ (10 หลัก)',
        'purposeOfUse': 'คุณจะใช้อุปกรณ์เพื่อวัตถุประสงค์อะไรครับ/ค่ะ?',
    }
    
    # English question templates
    en_templates = {
        'equipments': 'What type of equipment do you need? (e.g., Notebook, Desktop, Monitor)',
        'requestDate': 'What date would you like to receive the equipment?',
        'requestTime': 'What time would you like to pick up the equipment?',
        'deliveryLocation': 'Where should we deliver the equipment? (e.g., Srichand Building, Building A)',
        'department': 'What department are you in?',
        'position': 'What is your position?',
        'phoneNumber': 'What is your phone number? (10 digits)',
        'purposeOfUse': 'What will you be using the equipment for?',
    }
    
    templates = th_templates if language == "th" else en_templates
    
    # Check if we have a template for this field
    if field_name in templates:
        question = templates[field_name]
    else:
        # Generate generic question with enum options if available
        if 'enum' in field_def:
            options = field_def['enum']
            if language == "th":
                options_str = ', '.join(options)
                question = f"กรุณาระบุ {field_label} (ตัวเลือก: {options_str})"
            else:
                options_str = ', '.join(options)
                question = f"Please specify {field_label} (options: {options_str})"
        else:
            # Generic question
            if language == "th":
                question = f"กรุณาระบุ {field_label} ครับ/ค่ะ"
            else:
                question = f"Please provide {field_label}"
    
    # Add context-aware prefix for better conversation flow
    extracted_data = context.get('extracted_data', {})
    
    if extracted_data:
        if language == "th":
            prefix = "เข้าใจแล้วครับ/ค่ะ "
        else:
            prefix = "I understand. "
    else:
        prefix = ""
    
    return prefix + question
