from orchestrator import main

def get_function_name(code):
    for line in code.strip().splitlines():
        line = line.strip()
        if line.startswith("def "):
            return line.split("def ")[1].split("(")[0].strip()
    return "unknown_function"

def run():
    print("Paste your Python function below.")
    print("When done, type END on a new line and press Enter.")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    initial_code = "\n".join(lines)
    function_name = get_function_name(initial_code)
    print(f"\nFunction detected: {function_name}")

    print("\nRun with coverage guidance? (yes/no)")
    choice = input().strip().lower()
    with_coverage = choice == "yes"
    condition = "with_coverage" if with_coverage else "without_coverage"

    print(f"\nStarting experiment: {function_name} | {condition}\n")
    
    model_path = "qwen2.5-coder:7b"
    result = main(
        initial_code=initial_code,
        model_path=model_path,
        function_name=function_name,
        condition=condition,
        with_coverage=with_coverage
    )

    print("\nFinal validated code:")
    print(result)

if __name__ == "__main__":
    run()