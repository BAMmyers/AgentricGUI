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
pytest -v > test_results.txt

if %errorlevel% neq 0 (
    echo Tests failed. Check test_results.txt for details.
    exit /b 1
) else (
    echo Tests passed.
)

:: Run linter (assuming pylint is installed)
echo Checking code quality with pylint...
pylint app > pylint_results.txt
if %errorlevel% neq 0 (
    echo Linting issues found. Check pylint_results.txt for details.
) else (
    echo Code quality check passed.
)

echo All checks completed. Review the results in test_results.txt and pylint_results.txt.
pauseecho Running tests and checking for code quality...
echo. >> logs.txt
echo %date% %time% - Starting tests and code quality check >> logs.txt

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python.
    echo %date% %time% - Error: Python is not installed >> logs.txt
    exit /b 1
)

:: Activate the virtual environment
call venv\Scripts\activate.bat
echo %date% %time% - Virtual environment activated >> logs.txt

:: Run tests (assuming a test framework like pytest is used)
echo Running tests...
pytest -v > test_results.txt
echo %date% %time% - Tests completed >> logs.txt

if %errorlevel% neq 0 (
    echo Tests failed. Check test_results.txt for details.
    echo %date% %time% - Error: Tests failed >> logs.txt
    exit /b 1
)

:: Run linter (assuming pylint is installed)
echo Checking code quality with pylint...
pylint app > pylint_results.txt
echo %date% %time% - Code quality check completed >> logs.txt
if %errorlevel% neq 0 (
    echo Linting issues found. Check pylint_results.txt for details.
    echo %date% %time% - Error: Linting issues found >> logs.txt
)

echo All checks completed. Review the results in test_results.txt and pylint_results.txt.
echo %date% %time% - All checks completed >> logs.txt
pauseecho %date% %time% - Starting tests and code quality check >> logs.txt@echo off
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
pytest -v > test_results.txt

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
