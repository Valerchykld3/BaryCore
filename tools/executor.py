import os
import subprocess

def find_file(target_name: str, root_path: str) -> str:
    print(f"Searching '{target_name}' in '{root_path}'...")
    try:
        for root, dirs, files in os.walk(root_path):
            if target_name in files or target_name in dirs:
                return f"Success: {os.path.join(root, target_name).replace('\\', '/')}"
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