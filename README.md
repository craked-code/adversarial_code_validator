# code_validator
 
A multi-agent system for automated code validation using adversarial test generation, iterative refinement, and branch coverage guidance. Built with [Qwen 2.5 Coder 7B](https://ollama.com/library/qwen2.5-coder) running locally via [Ollama](https://ollama.com/).
 
---
 
## How It Works
 
The system consists of three agents operating in a loop:
 
**Generator** produces test cases for the current version of the code. **Adversary** attempts to find a failing input, optionally guided by which branches remain uncovered. **Refiner** fixes the code when the adversarial test fails. This loop continues until the code passes two consecutive adversarial tests while meeting a branch coverage threshold (when coverage guidance is enabled).
 
---
 
## Benchmark
 
To evaluate whether branch coverage guidance improves fault detection, we ran experiments on 10 Python functions, each containing a single intentionally injected bug. Each function was tested under two conditions: **with coverage guidance** (the Adversary is told which branches are uncovered) and **without coverage guidance** (the Adversary receives no structural information). Every condition was run with 5 independent random seeds to account for LLM non-determinism.
 
### Injected Bugs
 
| Function | Bug Description |
|---|---|
| `safe_divide` | Checks `b == 1` instead of `b == 0` for zero guard |
| `classify_triangle` | Equilateral check uses `a == b` instead of `a == b == c` |
| `fizzbuzz` | Uses `% 12` instead of `% 15` for fizzbuzz case |
| `find_max` | Checks `len == 1` instead of `len == 0` for empty list |
| `letter_grade` | B grade threshold is `>= 79` instead of `>= 80` |
| `is_leap_year` | Uses `% 200` instead of `% 400` for century leap year |
| `count_vowels` | Vowel set `"aeio"` is missing `'u'` |
| `temp_convert` | Fahrenheit-to-Celsius uses `(temp + 32)` instead of `(temp - 32)` |
| `clamp_value` | Upper bound check uses `>` instead of `>=` |
| `absolute_value` | Returns `-n` for positive numbers (swapped sign logic) |
 
---
 
## Results
 
All numbers are averages across 5 seeds per condition.
 
### Final Branch Coverage
 
| Function | With Coverage | Without Coverage |
|---|---|---|
| `safe_divide` | 100.0% | 0.0% |
| `classify_triangle` | 90.0% | 0.0% |
| `fizzbuzz` | 91.5% | 0.0% |
| `find_max` | 43.3% | 0.0% |
| `letter_grade` | 91.7% | 0.0% |
| `is_leap_year` | 90.7% | 0.0% |
| `count_vowels` | 75.0% | 0.0% |
| `temp_convert` | 60.0% | 0.0% |
| `clamp_value` | 91.7% | 0.0% |
| `absolute_value` | 93.3% | 0.0% |
| **Average** | **82.7%** | **0.0%** |
 
Coverage is 0% in the without-coverage condition by design — the system does not measure it, it simply does not use it.
 
### Bug Fix Rate (out of 5 seeds)
 
| Function | With Coverage | Without Coverage |
|---|---|---|
| `safe_divide` | 5/5 | 5/5 |
| `classify_triangle` | 5/5 | 1/5 |
| `fizzbuzz` | 5/5 | 1/5 |
| `find_max` | 4/5 | 2/5 |
| `letter_grade` | 5/5 | 0/5 |
| `is_leap_year` | 5/5 | 1/5 |
| `count_vowels` | 3/5 | 4/5 |
| `temp_convert` | 3/5 | 3/5 |
| `clamp_value` | 5/5 | 5/5 |
| `absolute_value` | 0/5 | 0/5 |
| **Total** | **40/50 (80%)** | **22/50 (44%)** |
 
### Key Observations
 
**Coverage guidance nearly doubled the bug fix rate** — 80% vs 44% across all seeds. For functions with subtle boundary bugs (`letter_grade`, `classify_triangle`, `is_leap_year`, `fizzbuzz`), the guided condition fixed the bug consistently while the baseline either failed entirely or only got lucky on one seed.
 
**`letter_grade` is the clearest example.** The bug (threshold at 79 instead of 80) only manifests for an input of exactly 79. Without coverage guidance, the adversary never discovered this input across all 5 seeds — 0/5 fixed. With coverage guidance, branch feedback directed the adversary toward the boundary, and all 5 seeds fixed the bug.
 
**`absolute_value` was unfixable under both conditions.** The bug (returning `-n` for positive numbers, making the function always negate its input) requires understanding what absolute value means. The 7B model consistently treated the behavior as correct and never generated a test that expected a positive output for a positive input. This is a model-capacity limitation rather than a failure of the coverage mechanism.
 
**`clamp_value` and `safe_divide` were fixed by both conditions equally.** For `safe_divide`, the bug (checking `b == 1` instead of `b == 0`) is caught quickly because dividing by zero crashes the executor, making it easy to discover without any structural guidance. For `clamp_value`, the `>=` vs `>` distinction is functionally invisible for most test inputs, so neither condition reliably exploited it — both fixed the structure of the function but not always the exact boundary behavior.
 
---
 
## Setup
 
**Requirements:** Python 3.10+, [Ollama](https://ollama.com/) installed locally, `coverage` and `qwen2.5-coder:7b` pulled via Ollama.
 
Install dependencies:
 
```
pip install coverage
ollama pull qwen2.5-coder:7b
```
 
**Run on your own function:**
 
```
python run_experiment.py
```
 
Paste your function, type END, choose whether to run with or without coverage guidance, and the system will validate it iteratively.
 
**Run the full benchmark:**
 
```
python run_benchmark.py
```
 
Results are saved as JSON files in the `experiment_logs/` folder.
 
---
 
## Project Structure
 
```
adversarial_code_validator/
├── agents/
│   ├── adversary.py         # Coverage-guided attack generation
│   ├── generator.py         # Baseline test case generation
│   └── refiner.py           # Code rewriting on failure
├── sandbox/
│   ├── executor.py          # Sandboxed code execution
│   └── coverage_runner.py   # Branch coverage measurement
├── experiment_logs/         # Auto-created; one JSON per run
├── orchestrator.py          # Entry point and loop controller
├── benchmark.py             # 10 intentionally buggy Python functions
├── run_benchmark.py         # Runs all 10 functions under both modes
├── run_experiment.py        # Interactive terminal tool — paste any function
├── combine_logs.py          # Aggregates experiment log files
├── graph.py                 # Visualises benchmark results
├── logger.py                # Structured JSON logging per run
└── all_results.json         # Aggregated benchmark output
```
 
---
 
## Model
 
All experiments used **Qwen 2.5 Coder 7B** running locally on CPU via Ollama. No external API calls are made. The model is the same for all three agents (Generator, Adversary, Refiner) across all conditions.
