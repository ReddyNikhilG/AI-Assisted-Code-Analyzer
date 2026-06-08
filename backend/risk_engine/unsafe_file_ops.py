from risk_engine.base_rule import RiskRule


class UnsafeFileOpsRule(RiskRule):
    name = "Unsafe File Operation"
    severity = "MEDIUM"

    # Functions that manipulate the filesystem dangerously
    destructive_functions = [
        "os.remove", "os.unlink", "os.rmdir",
        "shutil.rmtree", "shutil.move",
        "os.rename"
    ]

    def detect(self, root_node):
        findings = []

        def traverse(node):
            if node.type == "call":
                func_node = node.child_by_field_name("function")
                if func_node:
                    func_name = func_node.text.decode().strip()

                    # Check destructive file operations with dynamic paths
                    is_destructive = (
                        func_name in self.destructive_functions or
                        func_name in ("remove", "unlink", "rmdir", "rmtree", "move", "rename")
                    )
                    if is_destructive:
                        arguments = node.child_by_field_name("arguments")
                        if arguments:
                            for arg in arguments.children:
                                if arg.type not in ("(", ")", ",", "keyword_argument"):
                                    if arg.type != "string":
                                        findings.append({
                                            "type": self.name,
                                            "severity": self.severity,
                                            "code": node.text.decode(),
                                            "start_line": node.start_point[0] + 1,
                                            "start_column": node.start_point[1],
                                            "end_line": node.end_point[0] + 1,
                                            "end_column": node.end_point[1],
                                            "description": (
                                                f"'{func_name}' called with a dynamic path. "
                                                "Validate and sanitize the path to prevent path traversal attacks."
                                            )
                                        })
                                    break  # only check the first positional arg

                    # Check open() with dynamic path
                    elif func_name == "open":
                        arguments = node.child_by_field_name("arguments")
                        if arguments:
                            first_arg = None
                            for arg in arguments.children:
                                if arg.type not in ("(", ")", ",", "keyword_argument"):
                                    first_arg = arg
                                    break
                            if first_arg and first_arg.type != "string":
                                # Check if write/append mode
                                mode_arg = None
                                for arg in arguments.children:
                                    if arg.type == "keyword_argument":
                                        key = arg.child_by_field_name("name")
                                        if key and key.text.decode() == "mode":
                                            mode_arg = arg.child_by_field_name("value")
                                # Also check positional second arg
                                pos_count = 0
                                for arg in arguments.children:
                                    if arg.type not in ("(", ")", ",", "keyword_argument"):
                                        pos_count += 1
                                        if pos_count == 2:
                                            mode_arg = arg
                                            break

                                is_write = False
                                if mode_arg and mode_arg.type == "string":
                                    mode_text = mode_arg.text.decode().strip("'\"")
                                    if any(c in mode_text for c in ("w", "a", "x")):
                                        is_write = True

                                if is_write:
                                    findings.append({
                                        "type": self.name,
                                        "severity": "HIGH",
                                        "code": node.text.decode(),
                                        "start_line": node.start_point[0] + 1,
                                        "start_column": node.start_point[1],
                                        "end_line": node.end_point[0] + 1,
                                        "end_column": node.end_point[1],
                                        "description": (
                                            "open() in write mode with a dynamic path. "
                                            "Validate path to prevent arbitrary file write."
                                        )
                                    })
                                else:
                                    findings.append({
                                        "type": self.name,
                                        "severity": "MEDIUM",
                                        "code": node.text.decode(),
                                        "start_line": node.start_point[0] + 1,
                                        "start_column": node.start_point[1],
                                        "end_line": node.end_point[0] + 1,
                                        "end_column": node.end_point[1],
                                        "description": (
                                            "open() in read mode with a dynamic path. "
                                            "Validate path to prevent arbitrary file read (path traversal)."
                                        )
                                    })

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return findings
