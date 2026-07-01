import json
from collections.abc import Callable

# Import the raw JSON schemas you just converted
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file 
from functions.write_file import schema_write_file

# Import the actual callable functions
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

# Clean List structure instead of types.Tool
available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_run_python_file,
    schema_write_file,
]

function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

# --- The main helper ---
def call_function(tool_call, verbose: bool = False) -> dict:
    """
    Accepts an OpenAI ChatCompletionMessageToolCall object, 
    executes it locally, and structures a standard tool response dictionary.
    """
    function_name = tool_call.function.name or ""
    
    # Handle incoming arguments (OpenAI sends them as a JSON string)
    if isinstance(tool_call.function.arguments, str):
        try:
            args = json.loads(tool_call.function.arguments)
        except Exception:
            args = {}
    else:
        args = dict(tool_call.function.arguments) if tool_call.function.arguments else {}

    if verbose:
        print(f"Calling function: {function_name}({args})")
    else:
        print(f" - Calling function: {function_name}")

    # Check if the function exists in our map
    if function_name not in function_map:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps({"error": f"Unknown function: {function_name}"})
        }

    # Inject the working directory manually
    args["working_directory"] = "./calculator"

    try:
        # Call the actual Python execution function dynamically
        function_result = function_map[function_name](**args)
    except Exception as e:
        function_result = f"Error during local execution: {str(e)}"

    # Return standard OpenAI role='tool' message dictionary format
    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": function_name,
        "content": json.dumps({"result": function_result})
    }