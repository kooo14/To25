@echo off
setlocal

REM Python �̃C���X�g�[�����m�F
python --version
if %errorlevel% neq 0 (
    echo Python ���C���X�g�[������Ă��܂���B�C���X�g�[����A�ēx���s���Ă��������B
    exit /b 1
)

REM ���z���̗L�����m�F���A�Ȃ���΍쐬���ėL����
if exist "venv\Scripts\activate.bat" (
    echo ���z����ǂݍ��݂܂�...
    call "venv\Scripts\activate.bat"
) else (
    echo ���z����������܂���B�V�������z�����쐬���܂�...
    python -m venv venv
    python -m pip install --upgrade pip
    echo ���z����ǂݍ��݂܂�...
    call "venv\Scripts\activate.bat"
    REM Install required packages
    if exist "requirements.txt" (
        echo ���C�u�������C���X�g�[�����܂�...
        pip install -r requirements.txt
    ) else (
        echo requirements.txt ��������܂���B
    )
)


REM Run the main Python script
if exist "main.py" (
    echo ���C���X�N���v�g�����s���܂�...
    python main.py
) else (
    echo main.py ��������܂���B
)

endlocal
