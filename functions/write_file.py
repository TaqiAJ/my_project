import os
from google.genai import types

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)

        if not os.path.isabs(file_path):
            combined_path = os.path.join(abs_working_dir, file_path)
        else:
            combined_path = file_path
            
        abs_file_path = os.path.abspath(combined_path)

        if os.path.commonpath([abs_working_dir]) != os.path.commonpath([abs_working_dir, abs_file_path]):
            return f"Error: Cannot write to '{file_path}' as it is outside the permitted working directory"

        if os.path.isdir(abs_file_path):
            return f"Error: Cannot write to '{file_path}' as it is a directory"

        parent_dir = os.path.dirname(abs_file_path)
        os.makedirs(parent_dir, exist_ok=True)

        with open(abs_file_path, "w", encoding="utf-8") as file:
            file.write(content)

        return f"Successfully wrote to '{file_path}' ({len(content)} characters written)"
        
    except Exception as e:
        return f"Error: {str(e)}"


# --- ADD THE SCHEMA BELOW ---
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Creates a new file or overwrites an existing file with specific text content inside the workspace.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative destination path of the file to create or overwrite.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The raw text content or code to write into the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)