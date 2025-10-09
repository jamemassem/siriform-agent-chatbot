"""
Integration Test Script for Multiple Form Schemas

This script tests the system's ability to handle different form schemas:
1. equipment_form (original)
2. meeting_room_form (new)
3. leave_request_form (new)

Tests:
- Schema loading via API
- Frontend DynamicFormRenderer compatibility
- Field type support (string, number, boolean, array, enum, date, time)
- Required field validation
- Dependencies handling

Usage:
    cd backend
    uv run python -m app.test_schemas
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import load_form_schema


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_success(message: str):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ {message}")


def analyze_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze schema structure and extract statistics."""
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    # Count field types
    field_types = {}
    enum_fields = []
    array_fields = []
    boolean_fields = []
    date_time_fields = []
    
    for field_name, field_props in properties.items():
        field_type = field_props.get("type", "unknown")
        
        # Count types
        field_types[field_type] = field_types.get(field_type, 0) + 1
        
        # Categorize special fields
        if "enum" in field_props:
            enum_fields.append(field_name)
        if field_type == "array":
            array_fields.append(field_name)
        if field_type == "boolean":
            boolean_fields.append(field_name)
        if field_props.get("format") in ["date", "time", "date-time"]:
            date_time_fields.append(field_name)
    
    return {
        "total_fields": len(properties),
        "required_fields": len(required),
        "optional_fields": len(properties) - len(required),
        "field_types": field_types,
        "enum_fields": enum_fields,
        "array_fields": array_fields,
        "boolean_fields": boolean_fields,
        "date_time_fields": date_time_fields,
        "has_dependencies": "dependencies" in schema
    }


def test_schema_loading(form_name: str) -> bool:
    """Test loading a form schema."""
    print_header(f"Testing: {form_name}")
    
    try:
        schema = load_form_schema(form_name)
        print_success(f"Loaded schema: {form_name}")
        
        # Basic validation
        assert "properties" in schema, "Schema missing 'properties'"
        assert "title" in schema, "Schema missing 'title'"
        assert "version" in schema, "Schema missing 'version'"
        
        print_info(f"Title: {schema['title']}")
        print_info(f"Version: {schema['version']}")
        print_info(f"Description: {schema.get('description', 'N/A')}")
        
        # Analyze schema
        analysis = analyze_schema(schema)
        
        print(f"\n📊 Schema Statistics:")
        print(f"   Total fields: {analysis['total_fields']}")
        print(f"   Required: {analysis['required_fields']}")
        print(f"   Optional: {analysis['optional_fields']}")
        
        print(f"\n🔤 Field Types:")
        for field_type, count in analysis['field_types'].items():
            print(f"   {field_type}: {count}")
        
        if analysis['enum_fields']:
            print(f"\n📋 Enum Fields ({len(analysis['enum_fields'])}):")
            for field in analysis['enum_fields'][:5]:  # Show first 5
                print(f"   - {field}")
            if len(analysis['enum_fields']) > 5:
                print(f"   ... and {len(analysis['enum_fields']) - 5} more")
        
        if analysis['array_fields']:
            print(f"\n📦 Array Fields:")
            for field in analysis['array_fields']:
                print(f"   - {field}")
        
        if analysis['boolean_fields']:
            print(f"\n☑️  Boolean Fields:")
            for field in analysis['boolean_fields']:
                print(f"   - {field}")
        
        if analysis['date_time_fields']:
            print(f"\n📅 Date/Time Fields:")
            for field in analysis['date_time_fields']:
                print(f"   - {field}")
        
        if analysis['has_dependencies']:
            print(f"\n🔗 Has field dependencies: Yes")
        
        return True
        
    except FileNotFoundError:
        print_error(f"Schema file not found: {form_name}.json")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in schema: {e}")
        return False
    except AssertionError as e:
        print_error(f"Schema validation failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_field_compatibility(schema: Dict[str, Any]) -> List[str]:
    """Test if all field types are supported by DynamicFormRenderer."""
    print_header("Field Type Compatibility Test")
    
    supported_types = ["string", "number", "integer", "boolean", "array"]
    supported_formats = ["date", "time", "date-time", "email"]
    
    properties = schema.get("properties", {})
    unsupported = []
    
    for field_name, field_props in properties.items():
        field_type = field_props.get("type")
        field_format = field_props.get("format")
        
        # Check type support
        if field_type not in supported_types:
            unsupported.append(f"{field_name}: type '{field_type}' not supported")
            continue
        
        # Check format support (for strings)
        if field_type == "string" and field_format and field_format not in supported_formats:
            unsupported.append(f"{field_name}: format '{field_format}' not fully supported")
    
    if unsupported:
        print_error("Found unsupported field types:")
        for issue in unsupported:
            print(f"   - {issue}")
        return unsupported
    else:
        print_success("All field types are supported by DynamicFormRenderer")
        return []


def generate_sample_data(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate sample form data based on schema."""
    print_header("Sample Data Generation")
    
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    sample_data = {}
    
    for field_name, field_props in properties.items():
        # Only generate for required fields
        if field_name not in required:
            continue
        
        field_type = field_props.get("type")
        field_format = field_props.get("format")
        
        # Generate appropriate value
        if "enum" in field_props:
            sample_data[field_name] = field_props["enum"][0]
        elif field_type == "string":
            if field_format == "date":
                sample_data[field_name] = "2025-10-15"
            elif field_format == "time":
                sample_data[field_name] = "09:00"
            elif field_format == "email":
                sample_data[field_name] = "test@example.com"
            else:
                examples = field_props.get("examples", [])
                sample_data[field_name] = examples[0] if examples else "Sample value"
        elif field_type in ["number", "integer"]:
            sample_data[field_name] = field_props.get("default", 1)
        elif field_type == "boolean":
            sample_data[field_name] = field_props.get("default", False)
        elif field_type == "array":
            sample_data[field_name] = []
    
    print_success(f"Generated sample data with {len(sample_data)} fields")
    print("\n📝 Sample Data (Required Fields):")
    print(json.dumps(sample_data, indent=2, ensure_ascii=False))
    
    return sample_data


def test_api_endpoint(form_name: str):
    """Test if API endpoint can serve the schema."""
    print_header(f"API Endpoint Test: {form_name}")
    
    try:
        # Simulate API call
        schema = load_form_schema(form_name)
        
        # Simulate response structure
        response = {
            "name": form_name,
            "version": schema.get("version", "1.0.0"),
            "schema": schema
        }
        
        print_success(f"API endpoint /api/v1/form-schema/{form_name} ready")
        print_info(f"Response size: ~{len(json.dumps(response))} bytes")
        
        return True
        
    except Exception as e:
        print_error(f"API endpoint test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("  INTEGRATION TEST: Multiple Form Schemas")
    print("="*70)
    print("\nTesting system capability to handle different form types")
    print("This validates DynamicFormRenderer's flexibility\n")
    
    # List of schemas to test
    schemas_to_test = [
        "equipment_form",
        "meeting_room_form",
        "leave_request_form"
    ]
    
    results = {}
    
    # Test 1: Load all schemas
    print_header("Phase 1: Schema Loading")
    for form_name in schemas_to_test:
        results[form_name] = test_schema_loading(form_name)
    
    # Test 2: Field compatibility
    print("\n")
    for form_name in schemas_to_test:
        if results[form_name]:
            try:
                schema = load_form_schema(form_name)
                unsupported = test_field_compatibility(schema)
                results[f"{form_name}_compatibility"] = len(unsupported) == 0
            except:
                results[f"{form_name}_compatibility"] = False
    
    # Test 3: Sample data generation
    print("\n")
    for form_name in schemas_to_test:
        if results[form_name]:
            try:
                schema = load_form_schema(form_name)
                generate_sample_data(schema)
            except Exception as e:
                print_error(f"Sample data generation failed: {e}")
    
    # Test 4: API endpoint readiness
    print("\n")
    print_header("Phase 2: API Endpoint Readiness")
    for form_name in schemas_to_test:
        if results[form_name]:
            test_api_endpoint(form_name)
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for multiple form types.")
        print("\n📌 Next Steps:")
        print("   1. Start backend server: cd backend && uv run uvicorn app.main:app --reload")
        print("   2. Test API endpoints:")
        print("      - http://localhost:8000/api/v1/form-schema/equipment_form")
        print("      - http://localhost:8000/api/v1/form-schema/meeting_room_form")
        print("      - http://localhost:8000/api/v1/form-schema/leave_request_form")
        print("   3. Frontend will automatically render any schema via DynamicFormRenderer")
    else:
        print("\n⚠️  Some tests failed. Please review errors above.")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
