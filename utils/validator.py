def validate_schema(data: dict, schema: dict) -> bool:
    if not isinstance(data, dict):
        return False

    for key, expected_type in schema.items():
        if key not in data:
            return False
        if not isinstance(data[key], expected_type):
            return False

    return True
