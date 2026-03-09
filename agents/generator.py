import subprocess #to call a local LLM via command-line interface
import json #LLM response in text. We need structured data. LLM asked to output in json. This module pasrses the json output.

def strip_markdown(text):
    lines = text.strip().splitlines() #strip() removes extra whitespace or blanklines, [splitlines() by default splits at newline character putting it in a list]
    if lines[0].startswith("```"):
        lines = lines[1 : -1] #using pop would require calling pop twice with 2 positions of beginning and end, which is done in one line by slicing
        text = "\n".join(lines)
    return text.replace("'", '"')


class Generator:
    def __init__(self, model_path):
        self.model_path = model_path #stores path to the local LLM

    def generate(self, code): #takes code as a string, returns test cases
        prompt = f"Generate 3 test cases for this Python code. Return only valid JSON array format: [{{'input': ..., 'expected': ...}}]. Code:\n{code}" #text prompt that telss LLM exactly what to do
        cmd = ["ollama", "run", self.model_path, prompt] #command that will be passes to the subprocess: So it will execute: ollama run qwen2.5-coder:7b "your prompt"
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding="utf-8")
            '''
            capture_output=True : captures both stdout and stderr
            text=True : returns in string form instead of bytes
            timeout = 30 : prevents process from hanging indefinitely'''
            #print(f"DEBUG - stdout: {result.stdout}")
            #print(f"DEBUG - stderr: {result.stderr}")
            #print(f"DEBUG - return code: {result.returncode}")
            return json.loads(strip_markdown(result.stdout))
        except subprocess.TimeoutExpired:
            print("Generator: LLM timeout after 30s")
            return []
        except json.JSONDecodeError:
            print(f"Generator: Invalid JSON from LLM:")
            print(result.stdout)
            print("--- End of LLM output ---")
            return []
        except Exception as e:
            print(f"Generator: Unexpecter error: {e}")
            return[]