from risk_engine.sql_injection import SQLInjectionRule
from risk_engine.hardcoded_credentials import HardcodedCredentialRule
from risk_engine.dangerous_functions import DangerousFunctionRule
from risk_engine.command_injection import CommandInjectionRule
from risk_engine.unsafe_file_ops import UnsafeFileOpsRule


class RiskEngine:

    def __init__(self):
        self.rules = [
            SQLInjectionRule(),
            HardcodedCredentialRule(),
            DangerousFunctionRule(),
            CommandInjectionRule(),
            UnsafeFileOpsRule()
        ]

    def analyze(self, root_node):
        findings = []

        for rule in self.rules:
            findings.extend(rule.detect(root_node))

        return findings