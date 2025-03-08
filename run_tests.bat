@echo off
echo Running tests and checking for code quality...

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python.
    exit /b 1
)

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Run tests (assuming a test framework like pytest is used)
echo Running tests...
pytest > test_results.txt
if %errorlevel% neq 0 (
    echo Tests failed. Check test_results.txt for details.
    exit /b 1
)

:: Run linter (assuming pylint is installed)
echo Checking code quality with pylint...
pylint app > pylint_results.txt
if %errorlevel% neq 0 (
    echo Linting issues found. Check pylint_results.txt for details.
)

echo All checks completed. Review the results in test_results.txt and pylint_results.txt.
pause
