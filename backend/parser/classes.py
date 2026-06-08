def extract_classes(node):
    """Extract class definitions with name, bases, method count, and positions."""
    classes = []

    if node.type == "class_definition":
        name_node = node.child_by_field_name("name")
        if name_node:
            # Extract base classes from the argument_list (superclass_list)
            bases = []
            superclasses = node.child_by_field_name("superclasses")
            if superclasses:
                for child in superclasses.children:
                    if child.type not in ("(", ")", ","):
                        bases.append(child.text.decode())

            # Count methods defined inside the class body
            body = node.child_by_field_name("body")
            method_count = 0
            methods = []
            if body:
                for child in body.children:
                    if child.type == "function_definition":
                        method_count += 1
                        m_name = child.child_by_field_name("name")
                        if m_name:
                            methods.append(m_name.text.decode())

            classes.append({
                "name": name_node.text.decode(),
                "bases": bases,
                "methods": methods,
                "method_count": method_count,
                "start_line": node.start_point[0] + 1,
                "start_column": node.start_point[1],
                "end_line": node.end_point[0] + 1,
                "end_column": node.end_point[1]
            })

    for child in node.children:
        classes.extend(extract_classes(child))

    return classes
