import json
import os

class Logger:
    def __init__(self, function_name, condition):
        self.function_name = function_name
        self.condition = condition
        self.iterations = []
        self.final_coverage = 0.0
        self.total_iterations = 0
        self.final_code = ""
        self.bugs_found = []

    def log_iteration(self, iteration_num, coverage_pct, uncovered_branches, adversarial_passed):
        self.iterations.append({
            "iteration": iteration_num,
            "coverage_pct": coverage_pct,
            "uncovered_branches": uncovered_branches,
            "adversarial_passed": adversarial_passed
        })

    def log_final(self, final_coverage, total_iterations, final_code):
        self.final_coverage = final_coverage
        self.total_iterations = total_iterations
        self.final_code = final_code

    def log_bug_found(self, bug_name):
        self.bugs_found.append(bug_name)

    def save(self):
        os.makedirs("experiment_logs", exist_ok=True)
        filename = f"experiment_logs/{self.function_name}_{self.condition}.json"
        data = {
            "function_name": self.function_name,
            "condition": self.condition,
            "total_iterations": self.total_iterations,
            "final_coverage": self.final_coverage,
            "final_code": self.final_code,
            "bugs_found": self.bugs_found,
            "iterations": self.iterations
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Log saved to {filename}")