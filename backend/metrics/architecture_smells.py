import networkx as nx


def detect_smells(complexity_data, nesting_data=None, loc_data=None, call_graph=None):
    """
    Detect architecture smells from complexity metrics, nesting depth,
    lines-of-code, and call graph topology.
    """
    smells = []

    if nesting_data is None:
        nesting_data = {}
    if loc_data is None:
        loc_data = {}

    for function_name, complexity in complexity_data.items():
        # High Complexity Function (complexity > 10)
        if complexity > 10:
            smells.append({
                "function": function_name,
                "smell": "High Complexity",
                "severity": "HIGH",
                "detail": f"Cyclomatic complexity is {complexity} (threshold: 10). Consider refactoring."
            })
        elif complexity > 5:
            smells.append({
                "function": function_name,
                "smell": "Moderate Complexity",
                "severity": "MEDIUM",
                "detail": f"Cyclomatic complexity is {complexity} (threshold: 5). Monitor growth."
            })

    # God Function: LOC > 50
    for function_name, loc in loc_data.items():
        if loc > 50:
            smells.append({
                "function": function_name,
                "smell": "God Function",
                "severity": "HIGH",
                "detail": f"Function spans {loc} lines (threshold: 50). Break into smaller functions."
            })

    # Deep Nesting: depth > 4
    for function_name, depth in nesting_data.items():
        if depth > 4:
            smells.append({
                "function": function_name,
                "smell": "Deep Nesting",
                "severity": "MEDIUM",
                "detail": f"Maximum nesting depth is {depth} (threshold: 4). Use early returns or extract helpers."
            })

    # Excessive Fan-out: function calls > 8 distinct callees
    if call_graph and isinstance(call_graph, nx.DiGraph):
        for node in call_graph.nodes():
            out_degree = call_graph.out_degree(node)
            if out_degree > 8:
                smells.append({
                    "function": node,
                    "smell": "Excessive Fan-out",
                    "severity": "MEDIUM",
                    "detail": f"Function calls {out_degree} distinct functions (threshold: 8). Consider delegation."
                })

        # Cyclic Dependencies
        cycles = list(nx.simple_cycles(call_graph))
        for cycle in cycles:
            if len(cycle) > 1:
                smells.append({
                    "function": " → ".join(cycle),
                    "smell": "Cyclic Dependency",
                    "severity": "HIGH",
                    "detail": f"Circular call chain detected: {' → '.join(cycle)} → {cycle[0]}."
                })

    return smells