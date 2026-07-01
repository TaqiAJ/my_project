# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openai>=2.44.0",
#     "python-dotenv>=1.2.2",
# ]
# ///
import argparse
import os
import system_prompt
from dotenv import load_dotenv
from openai import OpenAI  # Use the OpenRouter-compatible SDK
import call_function  # Imports your call_function functions/helpers

def main() -> None:
    parser = argparse.ArgumentParser(description="AI Code Assistant") 
    parser.add_argument("user_prompt", type=str, help="Prompt to send to Gemini")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    
    api_key = os.environ.get("OPENROUTER_API_KEY") 
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    # Initialize the client pointing explicitly to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    messages = [
        {"role": "user", "content": args.user_prompt}
    ]
    
    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    generate_content(client, messages, args.verbose)


def generate_content(client: OpenAI, messages: list, verbose: bool) -> None:
    # We loop to allow consecutive tool calls (e.g., list files -> read file -> write file)
    while True:
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",  
            messages=[
                {"role": "system", "content": system_prompt.system_prompt},
                *messages
            ],
            tools=call_function.available_functions,  
            tool_choice="auto",
            max_tokens=1000
        )

        if not response.choices:
            raise RuntimeError("OpenRouter API response appears to be malformed")

        response_message = response.choices[0].message
        
        # Append the model's response (including its intent to call tools) to history
        messages.append(response_message)

        if verbose and response.usage:
            print(f"[Tokens used - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}]")

        # CASE 1: Gemini wants to call tools
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                # Execute the local function execution block
                function_call_result = call_function.call_function(tool_call, verbose=verbose)
                
                # Append the execution outcome back into the conversation history
                messages.append(function_call_result)
                
            # Continue the loop so the results are submitted back to Gemini
            print(" -> Sending tool output back to Gemini...")
            continue
            
        # CASE 2: No more tools to call, Gemini has provided a final text response
        else:
            print("\nFinal Agent Response:")
            print(response_message.content)
            break  # Exit the loop safely!


if __name__ == "__main__":
    main()