param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe"
)

& $PythonExe -m pytest -v test
exit $LASTEXITCODE
