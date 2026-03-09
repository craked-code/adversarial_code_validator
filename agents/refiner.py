import subprocess
import json

class Refiner:
    def __init__(self, model_path):
        self.model_path = model_path

    def refine(self, code, failing_test):
        prompt = f"Fix this code to pass the failing test. Return only the corrected Python code, no explanations. Failing test: {failing_test}. Code:\n{code}"
        cmd = ["ollama", "run", self.model_path, prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding="utf-8")
            return result.stdout.strip() #without json.load cause we want raw code unlike structured data for tests
        except subprocess.TimeoutExpired:
            print("Refiner: LLM timeout after 60s")
            return code
        except Exception as e:
            print(f"Refiner: Unexpted error: {e}")