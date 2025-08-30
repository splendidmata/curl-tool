@echo off
chcp 65001 >nul

echo ===============================
echo 开始构建Curl命令执行器EXE程序
echo ===============================

REM 检查是否安装了pip
echo 检查pip是否已安装...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pip未安装。请先安装Python并确保pip可用。
    pause
    exit /b 1
)

REM 安装所需依赖
echo 安装依赖包...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo 错误: 依赖包安装失败。
    pause
    exit /b 1
)

REM 打包成EXE文件
echo 正在打包成EXE文件...
pyinstaller --onefile --windowed --name=CurlCommandExecutor curl_executor.py
if %errorlevel% neq 0 (
    echo 错误: 打包过程失败。
    pause
    exit /b 1
)

REM 移动生成的EXE到根目录
echo 整理文件...
if exist "dist\CurlCommandExecutor.exe" (
    move "dist\CurlCommandExecutor.exe" . >nul
    echo EXE文件已生成: CurlCommandExecutor.exe
) else (
    echo 警告: 未找到生成的EXE文件。
)

REM 清理临时文件
echo 清理临时文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "CurlCommandExecutor.spec" del /q "CurlCommandExecutor.spec"

REM 显示完成信息
echo ===============================
echo 构建完成！
echo 您可以直接运行 "CurlCommandExecutor.exe" 文件使用程序

echo. 
echo 程序功能说明：
echo 1. 在文本框中输入您的curl命令

echo 2. 设置执行间隔时间（秒）
echo 3. 点击"开始执行"按钮开始重复执行命令

echo 4. 点击"停止执行"按钮停止执行

echo 5. 点击"清空输出"按钮清空输出窗口

echo. 
echo 注意事项：
echo - 确保您的系统已安装curl命令行工具

echo - 长时间运行可能会消耗系统资源

echo ===============================

pause