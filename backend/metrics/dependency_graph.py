import networkx as nx


def build_dependency_graph(imports):

    graph = nx.DiGraph()

    for imp in imports:
        # Handle dict format from our improved parser or raw string format
        imp_code = imp["code"] if isinstance(imp, dict) else imp

        cleaned = imp_code.strip()
        if cleaned.startswith("from"):
            # e.g., "from os import path" -> extract "os"
            parts = cleaned.split("import")
            module_part = parts[0].replace("from", "").strip()
            graph.add_edge("current_module", module_part)
        else:
            # e.g., "import sys, os" -> extract ["sys", "os"]
            module_part = cleaned.replace("import", "").strip()
            for sub_mod in module_part.split(","):
                mod_name = sub_mod.strip().split(" as ")[0].strip()
                if mod_name:
                    graph.add_edge("current_module", mod_name)

    return graph