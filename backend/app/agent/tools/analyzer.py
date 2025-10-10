"""Natural language request analyzer tool using LLM."""
from typing import Any, Dict, List, Optional
import re
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class EquipmentItem(BaseModel):
    """Equipment item extracted from user message."""
    type: str = Field(description="Type of equipment (Notebook, Desktop, Monitor, etc.)")
    quantity: int = Field(description="Quantity requested")
    detail: str = Field(default="", description="Additional details or specifications")


class ExtractedFormData(BaseModel):
    """Structured data extracted from user's natural language request."""
    equipments: Optional[List[EquipmentItem]] = Field(default=None, description="List of equipment items requested")
    requestDate: Optional[str] = Field(default=None, description="Requested date in YYYY-MM-DD format")
    requestTime: Optional[str] = Field(default=None, description="Requested time in HH:MM format")
    deliveryLocation: Optional[str] = Field(default=None, description="Delivery location or building")
    fullName: Optional[str] = Field(default=None, description="User's full name if mentioned")
    department: Optional[str] = Field(default=None, description="Department name if mentioned")
    purpose: Optional[str] = Field(default=None, description="Purpose or reason for request")


async def analyze_user_request(
    user_message: str,
    form_schema: Dict[str, Any],
    llm_client: Any
) -> Dict[str, Any]:
    """
    Analyze user's natural language request using LLM to extract structured information.
    
    This function uses LangChain + OpenRouter LLM to extract:
    - Equipment requests with quantities
    - Dates and times
    - Locations
    - Other form-relevant data
    
    Args:
        user_message: User's natural language input (Thai or English)
        form_schema: JSON Schema of the form to extract data for
        llm_client: LangChain LLM client (REQUIRED - will use OpenRouter)
        
    Returns:
        Dictionary containing:
        - extracted_data: Dict of field names to extracted values
        - confidence: Float between 0.0 and 1.0
        - ambiguities: List of fields that need clarification
    """
    if not llm_client:
        raise ValueError("llm_client is required for LLM-based analysis")
    
    # Create structured output parser
    parser = JsonOutputParser(pydantic_object=ExtractedFormData)
    
    # Create extraction prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert at extracting structured information from natural language requests in Thai and English.

Extract the following information from the user's message:
- Equipment requests (type, quantity, details)
- Date (convert relative dates like 'พรุ่งนี้'/'tomorrow' to YYYY-MM-DD)
- Time (convert 'เช้า'/'morning' to HH:MM format, e.g., 09:00)
- Location (building, room, department)
- User's name if mentioned
- Department if mentioned
- Purpose if mentioned

Today's date is: {today}

Return ONLY valid JSON matching this format:
{format_instructions}

If information is not mentioned, set the field to null."""),
        ("user", "{user_message}")
    ])
    
    # Get today's date for relative date conversion
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create chain
    chain = prompt | llm_client | parser
    
    try:
        print(f"🤖 Analyzer: Calling LLM with message: {user_message[:50]}...")
        
        # Invoke LLM to extract data
        result = await chain.ainvoke({
            "user_message": user_message,
            "today": today,
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"🤖 Analyzer: LLM returned: {result}")
        
        # Convert Pydantic models to dicts
        extracted_data = {}
        if result.get("equipments"):
            extracted_data["equipments"] = [
                {
                    "type": eq.type if isinstance(eq, EquipmentItem) else eq.get("type"),
                    "quantity": eq.quantity if isinstance(eq, EquipmentItem) else eq.get("quantity"),
                    "detail": eq.detail if isinstance(eq, EquipmentItem) else eq.get("detail", "")
                }
                for eq in result["equipments"]
            ]
        
        # Copy other fields if present
        for field in ["requestDate", "requestTime", "deliveryLocation", "fullName", "department", "purpose"]:
            if result.get(field):
                extracted_data[field] = result[field]
        
        # Determine ambiguities (fields that are null or missing)
        ambiguities = []
        required_fields = ["equipments", "requestDate", "requestTime", "deliveryLocation"]
        for field in required_fields:
            if field not in extracted_data or not extracted_data[field]:
                ambiguities.append(field)
        
        # Calculate confidence based on completeness
        filled_fields = len([f for f in required_fields if f in extracted_data and extracted_data[f]])
        confidence = filled_fields / len(required_fields)
        
        return {
            "extracted_data": extracted_data,
            "confidence": round(confidence, 2),
            "ambiguities": ambiguities
        }
        
    except Exception as e:
        print(f"❌ LLM extraction failed: {e}")
        # Fallback to empty extraction with low confidence
        return {
            "extracted_data": {},
            "confidence": 0.0,
            "ambiguities": ["equipments", "requestDate", "requestTime", "deliveryLocation"]
        }


# Keep old regex-based function as fallback
async def analyze_user_request_regex(
    user_message: str,
    form_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """Fallback regex-based analyzer (not used if LLM is available)."""
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
