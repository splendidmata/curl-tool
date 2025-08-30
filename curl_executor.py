import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import threading
import time
import sys
import os

class CurlExecutorApp:
    def __init__(self, root):
        # 设置中文字体支持
        self.root = root
        self.root.title("Bash格式Curl命令执行器")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 创建主题样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=('SimHei', 10))
        self.style.configure("TLabel", font=('SimHei', 10))
        
        # 初始化变量
        self.is_running = False
        self.execution_thread = None
        self.delay = tk.StringVar(value="1")  # 默认延迟1秒
        
        # 检测bash是否可用
        self.bash_available = self.check_bash_available()
        
        # 创建UI
        self.create_widgets()
    
    def check_bash_available(self):
        """检查系统是否安装了bash"""
        try:
            subprocess.run("bash --version", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # 尝试git bash路径
                git_bash_path = os.path.join(os.environ.get("PROGRAMFILES", "C:\Program Files"), "Git", "bin", "bash.exe")
                if os.path.exists(git_bash_path):
                    subprocess.run([git_bash_path, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return True
            except:
                pass
        return False
    
    def create_widgets(self):
        # 创建命令输入区域
        command_frame = ttk.LabelFrame(self.root, text="Bash格式Curl命令")
        command_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 添加提示标签
        hint_label = ttk.Label(command_frame, text="请输入bash格式的curl命令，例如:")
        hint_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        self.command_entry = scrolledtext.ScrolledText(command_frame, height=5, wrap=tk.WORD, font=('SimHei', 10))
        self.command_entry.pack(fill=tk.X, padx=5, pady=5)
        self.command_entry.insert(tk.END, "curl -X GET 'https://api.example.com/data' -H 'Authorization: Bearer token'")  # bash格式示例命令
        
        # 如果bash不可用，显示警告
        if not self.bash_available:
            warning_frame = ttk.Frame(self.root)
            warning_frame.pack(fill=tk.X, padx=10, pady=5)
            warning_label = ttk.Label(
                warning_frame, 
                text="警告: 未检测到bash环境! 请安装Git for Windows或WSL以运行bash命令。", 
                foreground="red"
            )
            warning_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # 创建控制区域
        control_frame = ttk.LabelFrame(self.root, text="控制选项")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 延迟输入
        ttk.Label(control_frame, text="执行间隔(秒):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.delay_entry = ttk.Entry(control_frame, textvariable=self.delay, width=10)
        self.delay_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=2, padx=20, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="开始执行", command=self.start_execution)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止执行", command=self.stop_execution, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="清空输出", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(self.root, text="执行结果")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=('SimHei', 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)
    
    def start_execution(self):
        # 检查bash是否可用
        if not self.bash_available:
            messagebox.showerror("错误", "未检测到bash环境! 请安装Git for Windows或WSL以运行bash命令。")
            return
            
        # 获取命令和延迟时间
        command = self.command_entry.get(1.0, tk.END).strip()
        
        if not command:
            messagebox.showerror("错误", "请输入bash格式的curl命令")
            return
        
        try:
            delay_seconds = float(self.delay.get())
            if delay_seconds <= 0:
                raise ValueError("延迟时间必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的延迟时间")
            return
        
        # 开始执行
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.delay_entry.config(state=tk.DISABLED)
        self.command_entry.config(state=tk.DISABLED)
        
        # 创建并启动执行线程
        self.execution_thread = threading.Thread(
            target=self.execute_command_loop, 
            args=(command, delay_seconds)
        )
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        self.append_output(f"[开始执行] {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def stop_execution(self):
        self.is_running = False
        if self.execution_thread and self.execution_thread.is_alive():
            # 等待线程结束
            self.execution_thread.join(timeout=1.0)
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.delay_entry.config(state=tk.NORMAL)
        self.command_entry.config(state=tk.NORMAL)
        
        self.append_output(f"[停止执行] {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def execute_command_loop(self, command, delay_seconds):
        while self.is_running:
            start_time = time.time()
            
            # 执行bash格式的命令
            try:
                # 构建通过bash执行的命令
                # 先尝试直接使用bash命令
                bash_cmd = f"bash -c \"{command}\""
                
                try:
                    # 尝试直接通过bash执行
                    process = subprocess.Popen(
                        bash_cmd, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                except:
                    # 尝试使用git bash的完整路径
                    git_bash_path = os.path.join(os.environ.get("PROGRAMFILES", "C:\Program Files"), "Git", "bin", "bash.exe")
                    if os.path.exists(git_bash_path):
                        process = subprocess.Popen(
                            [git_bash_path, "-c", command], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            text=True,
                            encoding='utf-8',
                            errors='replace'
                        )
                    else:
                        raise Exception("未找到bash可执行文件")
                
                output, _ = process.communicate(timeout=30)  # 30秒超时
                return_code = process.returncode
                
                self.append_output(f"[{time.strftime('%H:%M:%S')}] Bash命令执行结果 (返回码: {return_code}):\n{output}\n")
            except subprocess.TimeoutExpired:
                process.kill()
                self.append_output(f"[{time.strftime('%H:%M:%S')}] 命令执行超时 (30秒)\n")
            except Exception as e:
                self.append_output(f"[{time.strftime('%H:%M:%S')}] 执行出错: {str(e)}\n")
            
            # 计算需要等待的时间
            elapsed = time.time() - start_time
            wait_time = max(0, delay_seconds - elapsed)
            
            # 等待指定时间，但定期检查是否需要停止
            wait_intervals = 10  # 分成10个小段来检查停止信号
            for _ in range(wait_intervals):
                if not self.is_running:
                    break
                time.sleep(wait_time / wait_intervals)
    
    def append_output(self, text):
        # 在主线程中更新UI
        def update():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text)
            self.output_text.see(tk.END)  # 滚动到最新内容
            self.output_text.config(state=tk.DISABLED)
        
        # 确保在主线程中执行
        if self.root.winfo_exists():
            self.root.after(0, update)
    
    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    # 确保中文显示正常
    root = tk.Tk()
    app = CurlExecutorApp(root)
    root.mainloop()
