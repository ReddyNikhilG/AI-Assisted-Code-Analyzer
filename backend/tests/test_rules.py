import pytest
from tree_sitter import Language, Parser
import tree_sitter_python

from risk_engine.sql_injection import SQLInjectionRule
from risk_engine.command_injection import CommandInjectionRule
from risk_engine.dangerous_functions import DangerousFunctionRule
from risk_engine.hardcoded_credentials import HardcodedCredentialRule
from risk_engine.unsafe_file_ops import UnsafeFileOpsRule

PY_LANGUAGE = Language(tree_sitter_python.language())

def get_root_node(code: str):
    parser = Parser()
    parser.language = PY_LANGUAGE
    tree = parser.parse(code.encode("utf-8"))
    return tree.root_node

def test_sql_injection():
    rule = SQLInjectionRule()

    # True positive: dynamic concatenation
    code_tp = 'query = "SELECT * FROM users WHERE id = " + user_input'
    findings = rule.detect(get_root_node(code_tp))
    assert len(findings) == 1
    assert findings[0]["type"] == "SQL Injection"

    # True positive: f-string
    code_fstr = 'sql = f"SELECT * FROM users WHERE username = \'{user}\'"'
    findings = rule.detect(get_root_node(code_fstr))
    assert len(findings) == 1

    # False positive prevention: variable name containing keyword as substring
    code_fp = 'update_time = "Current time is: " + current_timestamp'
    findings = rule.detect(get_root_node(code_fp))
    assert len(findings) == 0

def test_command_injection():
    rule = CommandInjectionRule()

    # True positive: os.system fully qualified
    code_os_system = 'import os\nos.system(command)'
    findings = rule.detect(get_root_node(code_os_system))
    assert len(findings) == 1
    assert findings[0]["type"] == "Command Injection"

    # True positive: short name import
    code_short_system = 'from os import system\nsystem(command)'
    findings = rule.detect(get_root_node(code_short_system))
    assert len(findings) == 1

    # True positive: subprocess shell=True
    code_sub_shell = 'import subprocess\nsubprocess.run(command, shell=True)'
    findings = rule.detect(get_root_node(code_sub_shell))
    assert len(findings) == 1

    # True positive: subprocess run short name shell=True
    code_run_shell = 'from subprocess import run\nrun(command, shell=True)'
    findings = rule.detect(get_root_node(code_run_shell))
    assert len(findings) == 1

    # Safe call: list execution
    code_safe = 'from subprocess import run\nrun(["ls", "-l"])'
    findings = rule.detect(get_root_node(code_safe))
    assert len(findings) == 0

def test_dangerous_functions():
    rule = DangerousFunctionRule()

    # eval call
    findings = rule.detect(get_root_node('eval(code)'))
    assert len(findings) == 1

    # exec call
    findings = rule.detect(get_root_node('exec("import sys")'))
    assert len(findings) == 1

    # os.system fully qualified
    findings = rule.detect(get_root_node('os.system("ls")'))
    assert len(findings) == 1

    # system short name
    findings = rule.detect(get_root_node('from os import system\nsystem("ls")'))
    assert len(findings) == 1

def test_hardcoded_credentials():
    rule = HardcodedCredentialRule()

    # Assignment
    findings = rule.detect(get_root_node('password = "my-secret-pass"'))
    assert len(findings) == 1
    assert findings[0]["type"] == "Hardcoded Credential"

    # Dictionary key
    findings = rule.detect(get_root_node('credentials = {"api_key": "abc123xyz"}'))
    assert len(findings) == 1
    assert findings[0]["description"] == "Hardcoded credential assigned to 'api_key'."

    # Keyword argument
    findings = rule.detect(get_root_node('connect(db, token="secret_token")'))
    assert len(findings) == 1
    assert findings[0]["description"] == "Hardcoded credential assigned to 'token'."

    # False positive: non-literal value
    findings = rule.detect(get_root_node('password = get_pass()'))
    assert len(findings) == 0

def test_unsafe_file_operations():
    rule = UnsafeFileOpsRule()

    # Destructive function short name
    findings = rule.detect(get_root_node('from os import remove\nremove(dynamic_path)'))
    assert len(findings) == 1
    assert findings[0]["type"] == "Unsafe File Operation"

    # open write mode dynamic path (HIGH)
    findings = rule.detect(get_root_node('open(user_path, "w")'))
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"

    # open read mode dynamic path (MEDIUM)
    findings = rule.detect(get_root_node('open(user_path, "r")'))
    assert len(findings) == 1
    assert findings[0]["severity"] == "MEDIUM"

    # open read mode default mode (MEDIUM)
    findings = rule.detect(get_root_node('open(user_path)'))
    assert len(findings) == 1
    assert findings[0]["severity"] == "MEDIUM"

    # open read mode literal path (safe)
    findings = rule.detect(get_root_node('open("config.json")'))
    assert len(findings) == 0
