def calculate_complexity(node):
    """
    Calculate cyclomatic complexity of an AST node.
    Counts: if, elif, for, while, try, except, and/or boolean operators.
    """
    complexity = 1

    decision_nodes = [
        "if_statement",
        "elif_clause",
        "for_statement",
        "while_statement",
        "try_statement",
        "except_clause",
    ]

    boolean_operators = ["and", "or"]

    def traverse(current_node):
        nonlocal complexity

        if current_node.type in decision_nodes:
            complexity += 1

        if current_node.type == "boolean_operator":
            op = current_node.child_by_field_name("operator")
            if op and op.text.decode() in boolean_operators:
                complexity += 1

        for child in current_node.children:
            traverse(child)

    traverse(node)

    return complexity


def calculate_nesting_depth(node):
    """
    Calculate the maximum nesting depth of control-flow structures
    within an AST node.
    """
    nesting_types = {
        "if_statement", "for_statement", "while_statement",
        "try_statement", "with_statement"
    }

    def traverse(current_node, depth):
        current_depth = depth
        if current_node.type in nesting_types:
            current_depth = depth + 1

        max_depth = current_depth
        for child in current_node.children:
            child_depth = traverse(child, current_depth)
            if child_depth > max_depth:
                max_depth = child_depth

        return max_depth

    return traverse(node, 0)


def calculate_lines(node):
    """Calculate the number of source lines spanned by a node."""
    return (node.end_point[0] - node.start_point[0]) + 1