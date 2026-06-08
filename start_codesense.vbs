Set WshShell = CreateObject("WScript.Shell")
' Set working directory to the project root directory
WshShell.CurrentDirectory = "C:\Users\reddy\OneDrive\Documents\Projects\AI Assisted Code Analyzer"
' Run uvicorn with PYTHONPATH=backend, exactly mirroring our successful manual command
WshShell.Run "cmd.exe /c set PYTHONPATH=backend && backend\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000", 0, False
