from google.genai import types
from collections.abc import Callable

# Import the schemas for the tool definition (already present)
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file 
from functions.write_file import schema_write_file

# Import the actual callable functions (needed for execution)
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ],
)

function_map: dict[str, Callable[..., str]] = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

# --- The main helper ---
def call_function(
    function_call: types.FunctionCall, verbose: bool = False
) -> types.Content:
    # Print function name (and args if verbose)
    if verbose:
        print(f"Calling function: {function_call.name}{function_call.args}")
    else:
        print(f" - Calling function: {function_call.name}")

    # Safely get the function name (in case it's None)
    function_name = function_call.name or ""

    # Check if the function exists in our map
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Copy the arguments (or empty dict if None)
    args = dict(function_call.args) if function_call.args else {}

    # Overwrite working_directory
    args["working_directory"] = "./calculator"

    # Call the actual function with the (now modified) arguments
    function_result = function_map[function_name](**args)

    # Return the successful result
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )