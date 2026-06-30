from functions.run_python_file import run_python_file

def main():
    print("--- Test Case 1 ---")
    print(run_python_file("calculator", "main.py"))
    print("\n")

    print("--- Test Case 2 ---")
    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print("\n")

    print("--- Test Case 3 ---")
    print(run_python_file("calculator", "tests.py"))
    print("\n")

    print("--- Test Case 4 ---")
    print(run_python_file("calculator", "../main.py"))
    print("\n")

    print("--- Test Case 5 ---")
    print(run_python_file("calculator", "nonexistent.py"))
    print("\n")

    print("--- Test Case 6 ---")
    print(run_python_file("calculator", "lorem.txt"))
    print("\n")

if __name__ == "__main__":
    main()