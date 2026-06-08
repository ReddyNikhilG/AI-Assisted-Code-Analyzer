from risk_engine.base_rule import RiskRule


class HardcodedCredentialRule(RiskRule):
    name = "Hardcoded Credential"
    severity = "HIGH"

    suspicious_words = [
        "password",
        "secret",
        "token",
        "apikey",
        "api_key",
        "passwd"
    ]

    def detect(self, root_node):
        findings = []

        def traverse(node):
            left = None
            right = None

            if node.type == "assignment":
                left = node.child_by_field_name("left")
                if not left and len(node.children) > 0:
                    left = node.children[0]
                right = node.child_by_field_name("right")
                if not right and len(node.children) > 2:
                    right = node.children[2]
            elif node.type == "pair":
                left = node.child_by_field_name("key")
                right = node.child_by_field_name("value")
            elif node.type == "keyword_argument":
                left = node.child_by_field_name("name")
                right = node.child_by_field_name("value")

            if left and right:
                left_text = left.text.decode().lower().strip('"\' ')
                is_suspicious_var = any(word in left_text for word in self.suspicious_words)
                is_literal = (right.type == "string")

                if is_suspicious_var and is_literal:
                    val = right.text.decode().strip('"\'')
                    if len(val) > 0:
                        cred_name = left.text.decode().strip('"\' ')
                        findings.append({
                            "type": self.name,
                            "severity": self.severity,
                            "code": node.text.decode(),
                            "start_line": node.start_point[0] + 1,
                            "start_column": node.start_point[1],
                            "end_line": node.end_point[0] + 1,
                            "end_column": node.end_point[1],
                            "description": f"Hardcoded credential assigned to '{cred_name}'."
                        })

            for child in node.children:
                traverse(child)

        traverse(root_node)

        return findings