# code_validator


# AutoTestLoop 🔁

An autonomous multi-agent system that iteratively generates, attacks, and refines Python code using local LLMs — with optional branch coverage guidance to target untested logic paths. No human intervention required, no API keys, no cloud.


## What Is This?

AutoTestLoop is a self-contained pipeline that takes a piece of Python code and automatically stress-tests it to find breaking cases, then fixes the code when failures are discovered. It keeps looping until the code survives repeated adversarial attacks — or until a maximum iteration limit is reached.

The system supports two operating modes. In the standard mode, agents generate and attack tests freely. In the coverage-guided mode, the system measures which branches of the code have never been executed, and directs the adversary to specifically target those untested paths. This makes bug discovery significantly more systematic.

The entire system runs locally using [Ollama](https://ollama.com), meaning no API keys, no cloud costs, and no data leaving your machine.


## How It Works

The system is made up of four cooperating agents managed by a central orchestrator:

**1. Generator**
Looks at the current version of the code and produces three test cases. Each test case contains an input and the expected output. These are the baseline tests that describe what the code is supposed to do.

**2. Coverage Runner** *(optional, activated in coverage-guided mode)*
After the generator runs, the coverage runner executes all accumulated tests against the current code and measures branch coverage using Python's built-in coverage library. It returns two things — a percentage representing how much of the code's branching logic has been exercised, and a plain-English description of exactly which branches have never been taken. This information is passed directly to the adversary.

**3. Adversary**
Takes the current code, the recent test cases, and — in coverage-guided mode — the list of uncovered branches. It then tries to find a brand new test case that the code will fail, with priority given to inputs that force execution into those untested branches. This is the attacker — its job is to break things intelligently.

**4. Executor**
Runs the adversarial test case against the current code in a sandboxed environment. It reports back a simple pass or fail. The sandbox restricts which Python built-ins the code can access, preventing unsafe execution.

**5. Refiner**
If the adversarial test fails, the Refiner receives the broken code and the failing test, and rewrites the code to make it pass. The updated code then goes back into the next iteration.

**Orchestrator**
The orchestrator is the conductor. It initialises all agents, manages the loop, tracks consecutive passes and failures, monitors coverage progress, and decides when to stop. It also delegates logging to the Logger after every iteration.

**Logger**
Records every iteration's coverage percentage, uncovered branches, and whether the adversarial test passed or failed. At the end of each run, it saves a complete JSON log file into the experiment_logs folder, including the final code and a list of any bugs that were discovered.


## Project Structure

orchestrator.py is the main entry point and loop controller.

agents folder contains generator.py, adversary.py, and refiner.py — the three LLM-powered agents.

sandbox folder contains executor.py for safe sandboxed code execution, and coverage_runner.py for branch coverage measurement.

logger.py handles structured logging of every run to a JSON file.

benchmark.py contains ten intentionally buggy Python functions used to evaluate the system.

run_benchmark.py runs all ten benchmark functions under both conditions — with and without coverage guidance — and saves results to experiment_logs.

run_experiment.py is an interactive terminal tool that lets you paste in any Python function and run it through the pipeline.

experiment_logs folder is created automatically and stores one JSON file per run.


## Requirements

You need Python 3.8 or higher installed on your machine.

You need the coverage library installed. You can install it using pip with the package name "coverage".

You need [Ollama](https://ollama.com) installed and running locally.

You need the Qwen2.5-Coder 7B model pulled locally. You can pull it by running the Ollama pull command for qwen2.5-coder:7b in your terminal. Any other Ollama-compatible model can be substituted by changing the MODEL_PATH variable.


## How to Run

**To test your own function interactively**, run run_experiment.py using Python. It will ask you to paste a function, then ask whether you want to run with coverage guidance. It handles everything else automatically.

**To run the full benchmark**, run run_benchmark.py using Python. This will run all ten buggy functions from benchmark.py under both the with-coverage and without-coverage conditions, pausing briefly between runs. Results are saved to the experiment_logs folder as JSON files.


## Configuration

In run_benchmark.py, the MODEL_PATH variable sets which Ollama model to use. The MAX_ITERATIONS variable sets the maximum number of loop cycles per run. Both can be changed at the top of that file.

In orchestrator.py, the main function accepts a coverage_threshold parameter which defaults to 85.0. The loop will only converge when branch coverage meets or exceeds this threshold AND the adversary has passed two consecutive times.


## Stopping Conditions

The loop will stop when any one of the following happens:

The adversary passes two consecutive tests AND branch coverage meets or exceeds the threshold — meaning the code is considered both robust and well-exercised.

In without-coverage mode, the adversary simply needs to pass two consecutive tests.

The generator fails to produce valid tests three times in a row.

The adversary fails to produce a valid attack three times in a row.

The maximum iteration count is reached.


## Experiment Logs

Every run automatically saves a JSON file to the experiment_logs folder. The filename encodes the function name and condition, for example safe_divide_with_coverage.json.

Each log file contains the function name, condition, total iterations taken, final branch coverage percentage, the final version of the code after all refinements, a list of any bugs that were found and confirmed, and a full per-iteration breakdown showing coverage and adversarial test results at each step.


## The Benchmark

benchmark.py contains ten Python functions, each containing a single deliberately introduced bug. The bugs cover a range of common mistake types including off-by-one errors, wrong comparison operators, incorrect modular arithmetic, swapped logic, and missing edge case handling.

The benchmark is designed to test whether coverage-guided adversarial testing finds bugs faster and more reliably than unguided testing. Each function is run under both conditions so results can be directly compared.


## Limitations

The quality of test generation and code refinement depends entirely on the capability of the local model you choose. Smaller models may produce invalid JSON or incorrect fixes.

The executor sandbox restricts built-ins but is not a full security sandbox. It is not suitable for running untrusted or production code.

The system works best on small, single-function Python programs. Complex multi-function code may confuse the LLM agents.

Coverage measurement runs in the same process as the orchestrator. For very large or complex functions, this could occasionally produce inaccurate branch counts.


## Acknowledgements

Built using [Ollama](https://ollama.com) for local LLM inference. Default model is Qwen2.5-Coder 7B by Alibaba Cloud. Branch coverage powered by the Python [coverage.py](https://coverage.readthedocs.io) library.

---

## License

MIT License. Free to use, modify, and distribute.
