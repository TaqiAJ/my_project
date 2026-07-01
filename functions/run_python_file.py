import os
import subprocess

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        absolute_file_path = os.path.abspath(os.path.join(abs_working_dir, file_path))

        if not absolute_file_path.startswith(abs_working_dir + os.sep) and absolute_file_path != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(absolute_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", absolute_file_path]

        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            cwd=abs_working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        output_parts = []

        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")
            
        stdout_clean = result.stdout.strip() if result.stdout else ""
        stderr_clean = result.stderr.strip() if result.stderr else ""
        
        if not stdout_clean and not stderr_clean:
            output_parts.append("No output produced")
        else:
            if stdout_clean:
                output_parts.append(f"STDOUT:\n{stdout_clean}")
            if stderr_clean:
                output_parts.append(f"STDERR:\n{stderr_clean}")

        return "\n".join(output_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"


# Standard OpenAI/OpenRouter schema format
schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a specified Python script file within the workspace environment.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The relative path to the Python script to run.",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Optional list of command line arguments to pass to the script.",
                },
            },
            "required": ["file_path"],
        },
    }
}