from tree_sitter import Language, Parser
import tree_sitter_python

# -----------------------------
# Parser Extractors
# -----------------------------
from parser.functions import extract_functions
from parser.variables import extract_variables
from parser.imports import extract_imports
from parser.loops import extract_loops
from parser.calls import extract_calls
from parser.classes import extract_classes
from parser.decorators import extract_decorators

# -----------------------------
# Risk Engine
# -----------------------------
from risk_engine.engine import RiskEngine
from risk_engine.scoring import calculate_risk_score, calculate_risk_summary

# -----------------------------
# Intent Engine
# -----------------------------
from intent_engine.predictor import IntentPredictor

# -----------------------------
# Metrics / Architecture
# -----------------------------
from metrics.complexity import calculate_complexity, calculate_nesting_depth, calculate_lines
from metrics.call_graph import build_call_graph
from metrics.dependency_graph import build_dependency_graph
from metrics.architecture_smells import detect_smells

PY_LANGUAGE = Language(tree_sitter_python.language())


def get_parser():
    parser = Parser()
    parser.language = PY_LANGUAGE
    return parser


risk_engine = RiskEngine()
intent_predictor = IntentPredictor()


def analyze_code(code: str | bytes) -> dict:
    if isinstance(code, str):
        code_bytes = code.encode("utf-8")
        code_str = code
    else:
        code_bytes = code
        code_str = code.decode("utf-8", errors="replace")

    parser = get_parser()
    tree = parser.parse(code_bytes)
    root_node = tree.root_node

    # --- AST Extraction ---
    functions = extract_functions(root_node)
    variables = extract_variables(root_node)
    imports = extract_imports(root_node)
    loops = extract_loops(root_node)
    calls = extract_calls(root_node)
    classes = extract_classes(root_node)
    decorators = extract_decorators(root_node)

    # --- Risk Analysis ---
    risks = risk_engine.analyze(root_node)
    risk_score = calculate_risk_score(risks)
    risk_summary = calculate_risk_summary(risks)

    if risk_score == 0:
        risk_rating = "NONE"
    elif risk_score <= 4:
        risk_rating = "LOW"
    elif risk_score <= 8:
        risk_rating = "MEDIUM"
    elif risk_score <= 15:
        risk_rating = "HIGH"
    else:
        risk_rating = "CRITICAL"

    # --- Intent Prediction ---
    intent_result = intent_predictor.predict(code_str)

    # --- Complexity, Nesting, LOC ---
    complexity_data = {}
    nesting_data = {}
    loc_data = {}

    def extract_function_metrics(node):
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                func_name = name_node.text.decode()
                complexity_data[func_name] = calculate_complexity(node)
                nesting_data[func_name] = calculate_nesting_depth(node)
                loc_data[func_name] = calculate_lines(node)
        for child in node.children:
            extract_function_metrics(child)

    extract_function_metrics(root_node)

    # --- Call Graph & Dependency Graph ---
    call_graph = build_call_graph(root_node)
    dependency_graph = build_dependency_graph(imports)

    # --- Architecture Smells ---
    smells = detect_smells(complexity_data, nesting_data, loc_data, call_graph)

    return {
        # AST
        "functions": functions,
        "variables": variables,
        "imports": imports,
        "loops": loops,
        "loops_count": len(loops),
        "calls": calls,
        "classes": classes,
        "decorators": decorators,
        # Risk
        "risks": risks,
        "risk_score": risk_score,
        "risk_rating": risk_rating,
        "risk_summary": risk_summary,
        # Intent
        "intent_prediction": intent_result,
        # Metrics
        "complexity": complexity_data,
        "nesting_depth": nesting_data,
        "lines_of_code": loc_data,
        # Architecture
        "architecture_smells": smells,
        "call_graph_edges": list(call_graph.edges()),
        "dependency_graph_edges": list(dependency_graph.edges())
    }


if __name__ == "__main__":
    test_code = b"""
import os
from collections import OrderedDict

password = "admin123"

query = "SELECT * FROM users WHERE id = " + user_input

os.system(command)

class UserManager:
    def create_user(self, name):
        pass
    def delete_user(self, uid):
        os.remove(user_path)

@staticmethod
def validate():
    print("Validating")

def login():
    if password:
        for i in range(5):
            if i > 3 or i < 1:
                print(i)
    validate()
    eval(user_code)
"""
    result = analyze_code(test_code)
    import pprint
    pprint.pprint(result)