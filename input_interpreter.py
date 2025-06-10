import requests

def extract_properties(schema, swagger):
    """
    Recursively extract parameter names from schema definitions.
    Handles both direct properties and $ref resolution.
    """
    props = {}
    if "$ref" in schema:
        ref = schema["$ref"]
        ref_path = ref.strip("#/").split("/")
        for part in ref_path:
            swagger = swagger.get(part, {})
        return extract_properties(swagger, swagger)

    properties = schema.get("properties", {})
    for key, val in properties.items():
        props[key] = val.get("type", "string")

    return props

def extract_swagger_details(swagger_url):
    try:
        res = requests.get(swagger_url)
        swagger = res.json()
    except Exception as e:
        print("Failed to fetch or parse Swagger:", e)
        return [], {}

    endpoints = []
    all_params = {}

    paths = swagger.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if not isinstance(details, dict):
                continue

            # Add endpoint
            endpoints.append(f"{method.upper()} {path}")

            # Get path/query/header parameters
            parameters = details.get("parameters", [])
            for param in parameters:
                name = param.get("name")
                if name:
                    all_params[name] = param.get("in", "query")

            # ✅ NEW: Handle requestBody for OpenAPI 3.0
            request_body = details.get("requestBody", {})
            content = request_body.get("content", {})
            for media_type in content.values():
                schema = media_type.get("schema", {})
                body_props = extract_properties(schema, swagger)
                all_params.update(body_props)

    return endpoints, list(all_params.keys())
