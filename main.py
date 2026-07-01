import argparse
import os
import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions, call_function   # ← import call_function


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to Gemini")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    generate_content(client, messages, args.verbose)


def generate_content(
    client: genai.Client, messages: list[types.Content], verbose: bool
) -> None:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt.system_prompt,
            tools=[available_functions]
        ),
    )

    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed")

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    # Check if there are function calls
    if response.function_calls:
        function_results = []   # collect parts for later use

        for function_call in response.function_calls:
            # Step 10: call our helper instead of just printing
            function_call_result = call_function(function_call, verbose=verbose)

            # Validate the result
            if not function_call_result.parts:
                raise RuntimeError("Function call returned no parts.")
            func_response = function_call_result.parts[0].function_response
            if func_response is None:
                raise RuntimeError("Function response is None.")
            result_data = func_response.response
            if result_data is None:
                raise RuntimeError("Function response data is None.")

            # Store the part for later (if needed)
            function_results.append(function_call_result.parts[0])

            # Verbose output of the result (Step 10.5)
            if verbose:
                print(f"-> {result_data}")

        # (Optional) You could also print a summary of all results
        # For now, we just print them as they come (already done)
    else:
        # No function calls, just print the text response
        print(response.text)


if __name__ == "__main__":
    main()