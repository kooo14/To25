@echo off
chcp 65001
setlocal

python --version
if %errorlevel% neq 0 (
    echo Python not found.
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    echo Loading the virtual environment...
    call "venv\Scripts\activate.bat"
) else (
    echo Could not find the virtual environment.
    python -m venv venv
    echo Loading the virtual environment...
    call "venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    if exist "requirements.txt" (
        echo Installing the required packages...
        pip install -r requirements.txt
    ) else (
        echo requirements.txt not found.
    )
)


if exist "main.py" (
    echo Running main.py...
    python main.py
) else (
    echo main.py not found.
)

endlocal
