from risk_engine.base_rule import RiskRule


class DangerousFunctionRule(RiskRule):
    name = "Dangerous Function"
    severity = "HIGH"

    dangerous_calls = [
        "eval",
        "exec",
        "os.system"
    ]

    def detect(self, root_node):
        findings = []

        def traverse(node):
            if node.type == "call":
                func_node = node.child_by_field_name("function")
                if func_node:
                    func_name = func_node.text.decode().strip()
                    
                    matched_func = None
                    if func_name in self.dangerous_calls:
                        matched_func = func_name
                    elif func_name.startswith("os.system") or func_name == "system":
                        matched_func = "os.system"

                    if matched_func:
                        findings.append({
                            "type": self.name,
                            "severity": self.severity,
                            "code": node.text.decode(),
                            "start_line": node.start_point[0] + 1,
                            "start_column": node.start_point[1],
                            "end_line": node.end_point[0] + 1,
                            "end_column": node.end_point[1],
                            "description": f"Use of dangerous function '{matched_func}' detected."
                        })

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return findings