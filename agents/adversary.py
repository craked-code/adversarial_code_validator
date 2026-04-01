import subprocess
import json
from agents.generator import extract_json

class Adversary:
    def __init__(self, model_path):
        self.model_path = model_path

    def attack(self, code, existing_tests, uncovered_branches=""):
        if uncovered_branches:
            coverage_hint = f"The following branches are currently uncovered: {uncovered_branches}. Prioritize generating inputs that target these branches."
        else:
            coverage_hint = ""

        prompt = f"Find a breaking test case for this code. {coverage_hint} Existing tests: {existing_tests}. Return only valid JSON format: {{'input': ..., 'expected': ...}}. Code:\n{code}"
        cmd = ["ollama", "run", self.model_path, prompt]
        
        try:    
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8")
            parsed = extract_json(result.stdout)
            if parsed is None:
                print(f"Adversary: Invalid JSON from LLM: {result.stdout}")
                return None
            return parsed
        except subprocess.TimeoutExpired:
            print("Adversary: LLM timeout after 120s")
            return None
        except Exception as e:
            print(f"Adversary: Unexpected error: {e}")
            return None