import subprocess
import json
from agents.generator import strip_markdown

class Refiner:
    def __init__(self, model_path):
        self.model_path = model_path

    def refine(self, code, failing_test):
        prompt = f"Fix this code to pass the failing test. Return only a single Python function definition, no comments, no print statements, no duplicate functions, no explanations. Return only the raw Python code. Failing test: then {failing_test} then a period then Code: then \n then {code}"
        cmd = ["ollama", "run", self.model_path, prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, encoding="utf-8")
            return strip_markdown(result.stdout.strip()) #without json.load cause we want raw code unlike structured data for tests
        except subprocess.TimeoutExpired:
            print("Refiner: LLM timeout after 120s")
            return code
        except Exception as e:
            print(f"Refiner: Unexpected error: {e}")

        return code #refiner returns original code unchanged instead of None