param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe"
)

& $PythonExe -m pytest -v test/test_rest_api_functional.py
exit $LASTEXITCODE
