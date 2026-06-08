import re
from risk_engine.base_rule import RiskRule


class SQLInjectionRule(RiskRule):
    name = "SQL Injection"
    severity = "CRITICAL"

    sql_keywords = ["select", "insert", "update", "delete", "where"]

    def detect(self, root_node):
        findings = []

        def contains_sql_keyword(text):
            text_lower = text.lower()
            return any(re.search(r'\b' + re.escape(keyword) + r'\b', text_lower) for keyword in self.sql_keywords)

        def is_dynamic_sql(node):
            if node.type == "binary_operator":
                left = node.child_by_field_name("left")
                right = node.child_by_field_name("right")
                operator = node.child_by_field_name("operator")
                op_text = operator.text.decode() if operator else ""

                if op_text == "+":
                    left_text = left.text.decode() if left else ""
                    right_text = right.text.decode() if right else ""

                    left_is_str = left.type == "string" if left else False
                    right_is_str = right.type == "string" if right else False

                    if contains_sql_keyword(left_text) and not right_is_str:
                        return True
                    if contains_sql_keyword(right_text) and not left_is_str:
                        return True

            elif node.type == "string":
                text = node.text.decode()
                if text.startswith("f") or text.startswith("F"):
                    has_interpolation = any(child.type == "interpolation" for child in node.children)
                    if has_interpolation and contains_sql_keyword(text):
                        return True

            elif node.type == "call":
                func = node.child_by_field_name("function")
                if func and func.type == "attribute":
                    obj = func.child_by_field_name("object")
                    attr = func.child_by_field_name("attribute")
                    if obj and attr and attr.text.decode() == "format":
                        if obj.type == "string" and contains_sql_keyword(obj.text.decode()):
                            return True

            return False

        def traverse(node):
            if node.type == "assignment":
                right = node.child_by_field_name("right")
                if not right and len(node.children) > 2:
                    right = node.children[2]

                if right and (is_dynamic_sql(right) or any(is_dynamic_sql(c) for c in right.children)):
                    findings.append({
                        "type": self.name,
                        "severity": self.severity,
                        "code": node.text.decode(),
                        "start_line": node.start_point[0] + 1,
                        "start_column": node.start_point[1],
                        "end_line": node.end_point[0] + 1,
                        "end_column": node.end_point[1],
                        "description": "Dynamic SQL query construction detected. Use parameterized queries instead."
                    })

            elif node.type == "call":
                func = node.child_by_field_name("function")
                if func:
                    func_name = func.text.decode()
                    if "execute" in func_name:
                        arguments = node.child_by_field_name("arguments")
                        if arguments:
                            for arg in arguments.children:
                                if is_dynamic_sql(arg):
                                    findings.append({
                                        "type": self.name,
                                        "severity": self.severity,
                                        "code": node.text.decode(),
                                        "start_line": node.start_point[0] + 1,
                                        "start_column": node.start_point[1],
                                        "end_line": node.end_point[0] + 1,
                                        "end_column": node.end_point[1],
                                        "description": "Dynamic SQL query passed to execute() call. Use parameterized queries instead."
                                    })
                                    break

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return findings