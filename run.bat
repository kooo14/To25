@echo off
setlocal

REM Python のインストールを確認
python --version
if %errorlevel% neq 0 (
    echo Python がインストールされていません。インストール後、再度実行してください。
    exit /b 1
)

REM 仮想環境の有無を確認し、なければ作成して有効化
if exist "venv\Scripts\activate.bat" (
    echo 仮想環境を読み込みます...
    call "venv\Scripts\activate.bat"
) else (
    echo 仮想環境が見つかりません。新しい仮想環境を作成します...
    python -m venv venv
    python -m pip install --upgrade pip
    echo 仮想環境を読み込みます...
    call "venv\Scripts\activate.bat"
    REM Install required packages
    if exist "requirements.txt" (
        echo ライブラリをインストールします...
        pip install -r requirements.txt
    ) else (
        echo requirements.txt が見つかりません。
    )
)


REM Run the main Python script
if exist "main.py" (
    echo メインスクリプトを実行します...
    python main.py
) else (
    echo main.py が見つかりません。
)

endlocal
