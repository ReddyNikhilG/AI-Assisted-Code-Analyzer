def extract_decorators(node):
    """Extract decorators with name, target, and positions."""
    decorators = []

    if node.type == "decorated_definition":
        # The first children are decorator nodes, followed by the definition
        target_name = ""
        target_type = ""
        for child in node.children:
            if child.type == "decorator":
                # The decorator text is everything after '@'
                dec_text = child.text.decode().lstrip("@").strip()
                decorators.append({
                    "name": dec_text,
                    "start_line": child.start_point[0] + 1,
                    "start_column": child.start_point[1],
                    "end_line": child.end_point[0] + 1,
                    "end_column": child.end_point[1],
                    "target": "",  # filled below
                    "target_type": ""
                })
            elif child.type in ("function_definition", "class_definition"):
                name_node = child.child_by_field_name("name")
                target_name = name_node.text.decode() if name_node else ""
                target_type = "function" if child.type == "function_definition" else "class"

        # Assign the target to all decorators collected for this definition
        for dec in decorators:
            if not dec["target"]:
                dec["target"] = target_name
                dec["target_type"] = target_type

    for child in node.children:
        decorators.extend(extract_decorators(child))

    return decorators
