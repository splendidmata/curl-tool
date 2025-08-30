
        
        self.clear_button = ttk.Button(button_frame, text="清空输出", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(self.root, text="执行结果")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=('SimHei', 10))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)
    
    def start_execution(self):
        # 获取命令和延迟时间
        command = self.command_entry.get(1.0, tk.END).strip()
        
        if not command:
            messagebox.showerror("错误", "请输入curl命令")
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
            args=(command, delay_seconds, self.shell_type.get())
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
    
    def execute_command_loop(self, command, delay_seconds, shell_type):
        while self.is_running:
            start_time = time.time()
            
            # 执行命令，支持不同的shell类型
            try:
                # 根据shell类型处理命令
                if shell_type == "cmd":
                    # 处理cmd格式的多行命令，支持\和^作为行连接符
                    cmd_lines = command.splitlines()
                    processed_cmd = ""
                    for line in cmd_lines:
                        stripped_line = line.strip()
                        # 处理Windows cmd中的行连接符：^和\
                        if stripped_line.endswith('^'):
                            # 对于以^结尾的行，移除^并保留换行符
                            processed_cmd += stripped_line[:-1] + '\n'
                        elif stripped_line.endswith('\\'):
                            # 保留行尾的\，并添加换行符（cmd中的多行连接符）
                            processed_cmd += stripped_line + '\n'
                        else:
                            # 如果不是行连接符，则直接添加该行
                            processed_cmd += stripped_line + '\n'
                    # 移除最后的换行符
                    if processed_cmd.endswith('\n'):
                        processed_cmd = processed_cmd[:-1]
                    
                    # 使用cmd.exe执行命令
                    process = subprocess.Popen(
                        ['cmd.exe', '/c', processed_cmd], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                else:  # PowerShell
                    # 处理PowerShell格式的命令
                    # PowerShell使用反引号(`)作为行连接符，但这里我们统一处理所有情况
                    cmd_lines = command.splitlines()
                    processed_cmd = ""
                    for line in cmd_lines:
                        stripped_line = line.strip()
                        # PowerShell使用反引号(`)作为行连接符
                        if stripped_line.endswith('`'):
                            # 对于以`结尾的行，保留`并添加换行符
                            processed_cmd += stripped_line + '\n'
                        else:
                            # 如果不是行连接符，则直接添加该行
                            processed_cmd += stripped_line + '\n'
                    # 移除最后的换行符
                    if processed_cmd.endswith('\n'):
                        processed_cmd = processed_cmd[:-1]
                    
                    # 使用powershell.exe执行命令
                    process = subprocess.Popen(
                        ['powershell.exe', '-Command', processed_cmd], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                
                output, _ = process.communicate(timeout=30)  # 30秒超时
                return_code = process.returncode
                
                self.append_output(f"[{time.strftime('%H:%M:%S')}] 命令执行结果 (返回码: {return_code}):\n{output}\n")
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
