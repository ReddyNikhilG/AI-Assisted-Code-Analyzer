# 🛡️ CodeSense AI — Live Code Intent & Risk Analyzer

[![VS Code Extension](https://img.shields.io/badge/VS%20Code-Extension-blue?logo=visual-studio-code&logoColor=white&style=flat-square)](https://marketplace.visualstudio.com/)
[![FastAPI Backend](https://img.shields.io/badge/FastAPI-v2.0.0-009688?logo=fastapi&logoColor=white&style=flat-square)](http://127.0.0.1:8000)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white&style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Tree Sitter](https://img.shields.io/badge/AST%20Parser-Tree--Sitter-orange?style=flat-square)](https://tree-sitter.github.io/tree-sitter/)

CodeSense AI is a state-of-the-art, real-time code intelligence platform that combines **AST (Abstract Syntax Tree) parsing**, **heuristics-driven security analysis**, and **Machine Learning intent prediction** to provide instant feedback on Python code. 

With both an **interactive, premium web dashboard** and a **seamless VS Code Extension**, CodeSense AI acts as a 24/7 security auditor, quality linter, and architectural guide inside your workspace.

---

## 🚀 Key Features

*   **🔍 High-Fidelity AST Parsing**: Utilizes `tree-sitter` to perform instantaneous syntactic analysis, extracting functions, classes, decorators, imports, loop structures, variables, and function calls.
*   **🛡️ Multi-Rule Risk & Vulnerability Engine**: Detects common security issues:
    *   **SQL Injection**: Dynamic string concatenation and unsafe f-strings in SQL queries.
    *   **Command Injection**: Execution of shell commands (`os.system`, `subprocess` with `shell=True`).
    *   **Dangerous Functions**: Usage of dangerous functions like `eval()`, `exec()`, or `input()`.
    *   **Hardcoded Credentials**: Insecure assignment of secrets/passwords in variables, dictionaries, or keywords.
    *   **Unsafe File Operations**: Dynamic file paths, path traversal risks, and insecure file mode permissions.
*   **🤖 Intent Prediction (CodeBERT)**: Employs a pre-trained **CodeBERT** model (`microsoft/codebert-base`) and classifier to categorize code intention in real time (e.g., *API Communication, Database Operation, Computer Vision, Machine Learning, Networking, File Handling, Authentication, Web Server, or General Scripting*).
*   **📊 Complexity & Design Metrics**:
    *   **Cyclomatic Complexity**: Computes complexity score per function.
    *   **Nesting Depth**: Flags deeply nested loops and branches.
    *   **Lines of Code**: Measures method lengths to avoid monolithic codebases.
*   **🕸️ Interactive Call & Dependency Graphs**: Includes an interactive SVG-based force-directed graph visualizer in the dashboard. Drag nodes, highlight relationships, and hover to see immediate metrics for functions or import modules.
*   **🔌 VS Code Extension Integration**:
    *   **Live Analysis**: Runs debounced on-type (optional) or automatically on-save.
    *   **Diagnostics**: Underlines vulnerabilities and design smells directly in the editor.
    *   **Status Bar Integration**: Visual indicator showing the current file's safety level (None, Low, Medium, High, Critical) with contextual colors.
    *   **Rich Hovers**: Hover over functions to see their complexity table or hover over vulnerabilities to see details.
    *   **Offline Mode**: Gracefully handles disconnected states, notifying you with startup health checks.

---

## 📐 System Architecture

CodeSense AI uses a client-server architecture. The VS Code Extension and Web Dashboard act as clients, communicating asynchronously with a local FastAPI backend server:

```mermaid
graph TD
    subgraph Client Layer
        VSE[VS Code Extension]
        Dash[Interactive Glassmorphic Web Dashboard]
    end

    subgraph Backend API (FastAPI)
        API[FastAPI Router]
        Cache[In-Memory Deduplication Cache]
    end

    subgraph Analysis Engine
        AST[Tree-Sitter AST Parser]
        Risk[Heuristic Risk Engine]
        ML[CodeBERT Intent Engine]
        Metrics[Complexity & Design Evaluator]
        Graph[Call & Dependency Graph Generator]
    end

    VSE -- JSON POST /analyze --> API
    Dash -- JSON POST /analyze --> API
    API --> Cache
    Cache -- Cache Miss --> AST
    AST --> Risk
    AST --> ML
    AST --> Metrics
    AST --> Graph
    Risk --> API
    ML --> API
    Metrics --> API
    Graph --> API
    API -- JSON Response --> VSE
    API -- JSON Response --> Dash
```

---

## 📂 Repository Structure

```text
├── backend/
│   ├── parser/                 # AST Extractors (functions, variables, imports, loops, etc.)
│   ├── metrics/                # Complexity, Call/Dependency Graphs, Architecture Smells
│   ├── risk_engine/            # Security vulnerability analysis rules
│   ├── intent_engine/          # Machine learning classification dataset, model, and training scripts
│   ├── tests/                  # Pytest unit tests for APIs and rules
│   ├── main.py                 # FastAPI Web Server entrypoint
│   ├── index.html              # Dashboard frontend HTML/CSS/JS code
│   └── requirements.txt        # Python backend dependencies
├── vscode-extension/
│   ├── src/                    # Extension main scripts (extension.js, diagnostics.js, analyzer.js)
│   ├── package.json            # Extension configuration & command registrations
│   └── codesense-ai-1.0.0.vsix # Packaged VS Code extension
├── start_codesense.vbs         # Windows background startup script
└── README.md                   # This documentation
```

---

## 🛠️ Installation & Getting Started

### Prerequisites
*   **Python**: Version 3.8 or higher.
*   **Node.js**: Required to rebuild or debug the VS Code extension.
*   **VS Code**: VS Code IDE.

---

### Step 1: Set Up & Run the Backend

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**:
    *   **Windows (PowerShell)**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **macOS / Linux**:
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Server**:
    ```bash
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    ```
    Alternatively on Windows, you can double-click **`start_codesense.vbs`** in the project root to run the backend silently in the background.

6.  **Open Dashboard**:
    Navigate to `http://127.0.0.1:8000` to interact with the glassmorphism dashboard.

---

### Step 2: Set Up the VS Code Extension

To install the custom extension in your VS Code IDE:

1.  **Install the Pre-packaged Extension**:
    *   Open VS Code.
    *   Go to **Extensions** view (`Ctrl+Shift+X` or `Cmd+Shift+X`).
    *   Click on the **Views and More Actions** (`...`) icon at the top right of the Extensions panel.
    *   Select **Install from VSIX...**.
    *   Choose the packaged file: `vscode-extension/codesense-ai-1.0.0.vsix`.

2.  **Development Mode (Optional)**:
    If you want to modify or run the extension code directly:
    *   Navigate to the extension directory: `cd vscode-extension`.
    *   Open it in a new VS Code window: `code .`.
    *   Press `F5` to open a new **Extension Development Host** window.
    *   Open any `.py` file to test live analysis!

---

## 💡 Usage Guide

### Using the Web Dashboard
*   Paste any Python snippet into the **Source Code Input** editor.
*   Click **Analyze Code**.
*   View:
    *   **Vulnerability Alerts** categorizing security risks by severity (Low, Medium, High, Critical).
    *   **Predicted Intent** showcasing the ML-powered intent category along with top confidence scores.
    *   **AST Elements** tabs showing classes, methods, parameters, and variable definitions.
    *   **Call & Dependency Graphs** visualizer. Hover, drag, and click node variables to visualize architectural structure.

### Using the VS Code Extension
*   **Debounced Analysis**: CodeSense analyzes files as you type. If you prefer to disable this, change `"codesense.analyzeOnType"` to `false` in VS Code settings.
*   **Analyze on Save**: Runs analysis automatically every time you save a `.py` file.
*   **Status Bar**: Check the status bar at the bottom. E.g., `(flame) CodeSense: HIGH` or `(check) CodeSense: NONE`. Hovering over this details the precise risk score.
*   **Diagnostics**: Hover over highlighted issues inside a Python file to view direct explanations or Cyclomatic Complexity tables.
*   **Commands**:
    *   `CodeSense: Analyze Current File` — Manually trigger code analysis on the open document.
    *   `CodeSense: Open Dashboard` — Instantly opens the interactive web dashboard in your browser.

---

## ⚙️ Configuration Settings

Customize the VS Code extension by searching `CodeSense AI` in VS Code settings:

| Setting Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `codesense.backendUrl` | String | `http://127.0.0.1:8000` | Endpoint of the FastAPI backend. |
| `codesense.analyzeOnSave` | Boolean | `true` | Automatically runs analysis upon file saves. |
| `codesense.analyzeOnType` | Boolean | `true` | Runs live analysis while typing. |
| `codesense.debounceMs` | Number | `1000` | Delay (in milliseconds) for debouncing on-type analysis. |

---

## 🧪 Testing

The repository contains a full testing suite running on `pytest`. 

To run all backend API and security rule tests, make sure your virtual environment is active, navigate to the `backend` directory, and run:

```bash
pytest
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.