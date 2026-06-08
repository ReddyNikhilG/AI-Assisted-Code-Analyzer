from risk_engine.base_rule import RiskRule


class CommandInjectionRule(RiskRule):
    name = "Command Injection"
    severity = "CRITICAL"

    # Functions where shell=True or dynamic args are dangerous
    dangerous_commands = [
        "os.system", "os.popen",
        "subprocess.call", "subprocess.run",
        "subprocess.Popen", "subprocess.check_output",
        "subprocess.check_call"
    ]

    cmd_mapping = {
        "os.system": "os.system",
        "system": "os.system",
        "os.popen": "os.popen",
        "popen": "os.popen",
        "subprocess.call": "subprocess.call",
        "call": "subprocess.call",
        "subprocess.run": "subprocess.run",
        "run": "subprocess.run",
        "subprocess.Popen": "subprocess.Popen",
        "Popen": "subprocess.Popen",
        "subprocess.check_output": "subprocess.check_output",
        "check_output": "subprocess.check_output",
        "subprocess.check_call": "subprocess.check_call",
        "check_call": "subprocess.check_call"
    }

    def detect(self, root_node):
        findings = []

        def traverse(node):
            if node.type == "call":
                func_node = node.child_by_field_name("function")
                if func_node:
                    func_name = func_node.text.decode().strip()
                    normalized_func = self.cmd_mapping.get(func_name)

                    if normalized_func:
                        arguments = node.child_by_field_name("arguments")
                        is_dangerous = False
                        reason = ""

                        if normalized_func in ("os.system", "os.popen"):
                            # These are always dangerous with non-literal args
                            if arguments:
                                for arg in arguments.children:
                                    if arg.type not in ("(", ")", ",") and arg.type != "string":
                                        is_dangerous = True
                                        reason = f"'{func_name}' called with dynamic argument. Use subprocess with a list instead."
                                        break
                                # Even with literal, os.system is risky
                                if not is_dangerous:
                                    is_dangerous = True
                                    reason = f"'{func_name}' is inherently unsafe. Use subprocess with shell=False."

                        elif normalized_func.startswith("subprocess."):
                            # Check for shell=True keyword arg
                            if arguments:
                                for arg in arguments.children:
                                    if arg.type == "keyword_argument":
                                        key = arg.child_by_field_name("name")
                                        value = arg.child_by_field_name("value")
                                        if key and value:
                                            if key.text.decode() == "shell" and value.text.decode() == "True":
                                                is_dangerous = True
                                                reason = f"'{func_name}' called with shell=True. This enables shell injection."
                                                break

                        if is_dangerous:
                            findings.append({
                                "type": self.name,
                                "severity": self.severity,
                                "code": node.text.decode(),
                                "start_line": node.start_point[0] + 1,
                                "start_column": node.start_point[1],
                                "end_line": node.end_point[0] + 1,
                                "end_column": node.end_point[1],
                                "description": reason
                            })

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return findings
