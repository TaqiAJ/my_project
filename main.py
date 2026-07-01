import argparse
import os
import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from call_function import available_functions, call_function


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

    # Initialize conversation with the user's prompt
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    # Reusable config (system instruction + tools)
    config = types.GenerateContentConfig(
        system_instruction=system_prompt.system_prompt,
        tools=[available_functions],
    )

    # Main agent loop – max 20 iterations
    for iteration in range(20):
        if args.verbose:
            print(f"\n--- Iteration {iteration + 1} ---")

        # 1. Call the model with the current conversation
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=config,
        )

        # 2. Append the model's response(s) to the conversation
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)
        else:
            print("No candidates in response. Exiting.")
            break

        # 3. Check if the model requested function calls
        if response.function_calls:
            # Collect tool response parts from each function call
            tool_parts = []
            for function_call in response.function_calls:
                result_content = call_function(function_call, verbose=args.verbose)

                # Validate the result (should have a non‑empty parts list)
                if not result_content.parts:
                    raise RuntimeError("Function call returned no parts.")

                # We expect exactly one part (the function response)
                # Add it to the list of tool parts
                tool_parts.append(result_content.parts[0])

            # 4. Append the tool results as a new user message
            messages.append(types.Content(role="user", parts=tool_parts))

        else:
            if response.text:
                print("Final response:")
                print(response.text)
            else:
                print("No response text from model.")
            break
    else:
        print("Maximum iterations (20) reached without final response.")
        exit(1)


if __name__ == "__main__":
    main()