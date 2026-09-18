import os
import subprocess
import shutil
import psutil
from send2trash import send2trash
from datetime import datetime

# Tools for DFMB

def list_directory(path: str) -> str:
    print(f"Listing directory: {path}")
    try:
        items = os.listdir(path)
        return f"Contents of {path}:\n" + "\n".join(items[:50])
    except Exception as e:
        return f"List error: {str(e)}"

def find_file(target_name: str, root_path: str) -> str:
    print(f"Searching '{target_name}' in '{root_path}'...")
    target_lower = target_name.lower()
    try:
        for root, dirs, files in os.walk(root_path):
            for item in files + dirs:
                if target_lower in item.lower():
                    return f"Success: {os.path.join(root, item).replace('\\', '/')}"
        return f"Error: '{target_name}' not found."
    except Exception as e:
        return f"Access error: {str(e)}"

def read_file_content(filepath: str) -> str:
    print(f"Reading file '{filepath}'...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = "".join(lines[:100])
            if len(lines) > 100:
                content += "\n... (context economy)"
            return f"File content:\n{content}"
    except Exception as e:
        return f"Read error: {str(e)}"

def create_directory(path: str) -> str:
    print(f"Creating directory: {path}")
    try:
        os.makedirs(path, exist_ok=True)
        return f"Success: Directory created at '{path}'"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

def create_file(path: str, content: str = "") -> str:
    print(f"Creating file: {path}")
    try:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: File created at '{path}'"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def edit_file(filepath: str, mode: str, new_content: str, old_content: str = "") -> str:
    print(f"Editing file '{filepath}' in mode '{mode}'...")
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        
        if mode == 'append':
            with open(filepath, 'a', encoding='utf-8') as f:
                # Додаємо новий рядок, щоб текст не злипався з попереднім
                f.write("\n" + new_content)
            return f"Success: Appended new content to '{filepath}'."
            
        elif mode == 'overwrite':
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"Success: Completely overwrote the content of '{filepath}'."
            
        elif mode == 'replace':
            with open(filepath, 'r', encoding='utf-8') as f:
                file_data = f.read()
                
            if old_content not in file_data:
                return "Error: The exact 'old_content' was not found in the file. No changes made."
                
            file_data = file_data.replace(old_content, new_content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_data)
            return f"Success: Replaced specific content in '{filepath}'."
            
        else:
            return "Error: Invalid mode. Use 'append', 'overwrite', or 'replace'."
    except Exception as e:
        return f"Edit error: {str(e)}"

def copy_item(src: str, dst: str) -> str:
    try:
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return f"Success: Copied '{src}' to '{dst}'"
    except Exception as e:
        return f"Copy error: {str(e)}"

def move_item(src: str, dst: str) -> str:
    try:
        shutil.move(src, dst)
        return f"Success: Moved '{src}' to '{dst}'"
    except Exception as e:
        return f"Move error: {str(e)}"

def delete_item(path: str) -> str:
    print(f"Attempting to trash item: {path}")
    try:
        if not os.path.exists(path):
            return f"Error: '{path}' does not exist."
            
        send2trash(path)
        return f"Success: Moved '{path}' to the recycle bin."
    except Exception as e:
        return f"Delete error: {str(e)}"

def get_file_info(path: str) -> str:
    try:
        stats = os.stat(path)
        size_mb = stats.st_size / (1024 * 1024)
        created = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        is_dir = "Directory" if os.path.isdir(path) else "File"
        return f"Info for {path}:\nType: {is_dir}\nSize: {size_mb:.2f} MB\nCreated: {created}\nModified: {modified}"
    except Exception as e:
        return f"Info error: {str(e)}"

# Tools for DTRB

def execute_shell_command(command: str) -> str:
    print(f"Executing command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            return f"Success (stdout):\n{result.stdout[:1000]}"
        if result.stderr:
            return f"Execution error (stderr):\n{result.stderr[:1000]}"
        return "Command executed successfully (no output)."

    except Exception as e:
        return f"Critical terminal error: {str(e)}"

def check_process_status(process_name: str) -> str:
    print(f"Checking status for process: {process_name}")
    try:
        found_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                found_processes.append(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Status: {proc.info['status']}")

        if found_processes:
            return "Found active processes:\n" + "\n".join(found_processes)
        return f"No active processes found matching '{process_name}'."
    except Exception as e:
        return f"Error checking process status: {str(e)}"

def kill_process(pid_or_name: str) -> str:
    print(f"Attempting to kill process: {pid_or_name}")
    try:
        killed = []
        if pid_or_name.isdigit():
            pid = int(pid_or_name)
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                name = p.name()
                p.terminate()
                return f"Success: Terminated process {name} (PID: {pid})"
            return f"Error: Process with PID {pid} not found."
        
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and pid_or_name.lower() == proc.info['name'].lower():
                    proc.terminate()
                    killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")

            if killed:
                return "Success: Terminated the following processes:\n" + "\n".join(killed)
            return f"Error: No process found with exact name '{pid_or_name}'."
    except Exception as e:
        return f"Error terminating process: {str(e)}"

def get_system_resources() -> str:
    print("Fetching system resources...")
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        ram_total = ram.total / (1024 ** 3)
        ram_used = ram.used / (1024 ** 3)

        return (f"System Resources:\n"
                f"CPU Usage: {cpu_usage}%\n"
                f"RAM Usage: {ram_usage}% ({ram_used:.2f} GB / {ram_total:.2f} GB)")
    except Exception as e:
        return f"Error fetching system resources: {str(e)}"