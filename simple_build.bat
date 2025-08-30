@echo off

REM 尝试使用python -m pip安装pyinstaller
python -m pip install pyinstaller

REM 如果上面的命令失败，尝试使用python3
if %errorlevel% neq 0 (
    python3 -m pip install pyinstaller
)

REM 如果安装成功，尝试打包
if %errorlevel% equ 0 (
    python -m PyInstaller --onefile --windowed --name=CurlExecutor curl_executor.py
    if %errorlevel% neq 0 (
        python3 -m PyInstaller --onefile --windowed --name=CurlExecutor curl_executor.py
    )

    REM 检查是否生成了EXE文件
    if exist "dist\CurlExecutor.exe" (
        echo.
        echo 构建成功！
        echo EXE文件位置: dist\CurlExecutor.exe
    ) else (
        echo.
        echo 构建失败！请手动安装pyinstaller并运行以下命令：
        echo python -m PyInstaller --onefile --windowed --name=CurlExecutor curl_executor.py
    )
) else (
    echo.
    echo 无法安装pyinstaller！请确保Python已正确安装。
    echo 手动安装方法：
    echo 1. 打开命令提示符
    echo 2. 运行: python -m pip install pyinstaller
    echo 3. 然后运行: python -m PyInstaller --onefile --windowed --name=CurlExecutor curl_executor.py
)

pause