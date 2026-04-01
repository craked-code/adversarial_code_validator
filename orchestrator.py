#entry point that imports from agent and sandbox

from agents.generator import Generator
from agents.adversary import Adversary
from agents.refiner import Refiner
from sandbox.executor import execute_test
from sandbox.coverage_runner import get_coverage
from logger import Logger

def main(initial_code, model_path, function_name="test_function", condition="with_coverage", with_coverage=True, max_iterations=10, coverage_threshold=85.0):
    #intantiating
    generator = Generator(model_path)
    adversary = Adversary(model_path)
    refiner = Refiner(model_path)

    current_code = initial_code
    all_tests = [] #to collect every test generated across all iterations
    iteration = 0
    consecutive_generator_failures = 0
    consecutive_adversary_failures = 0
    consecutive_passes = 0 
    current_coverage = 0.0
    logger = Logger(function_name, condition)
    uncovered_branches = ""

    while iteration < max_iterations:
        print(f"\n-- Iteration {iteration + 1} --")
        tests = generator.generate(current_code)
        if not tests:
            consecutive_generator_failures += 1 
            if consecutive_generator_failures >=3:
                print("Generator failed 3 times in a row. Aborting.")
                break
            iteration += 1
            continue
        else: 
            consecutive_generator_failures = 0
        
        print(f"Generator produced {len(tests)} test(s)")
        all_tests.extend(tests) #we use extend instead of append because test is already a list
        '''
        we do not need to keep track of which test was generated at which iteration
        the goal of all_tests is to answer one question during convergence — 
        "does the current code pass every test we have ever seen?"
        '''

        if with_coverage:
            current_coverage, uncovered_branches = get_coverage(current_code, all_tests)
            #print("DEBUG current code:", current_code)
            print(f"Branch coverage: {current_coverage}% | Uncovered: {uncovered_branches}")
        else:
            current_coverage, uncovered_branches = 0.0, ""

        adversarial_tests = adversary.attack(current_code, all_tests[-5:], uncovered_branches)
        if adversarial_tests is None:
            consecutive_adversary_failures += 1
            if consecutive_adversary_failures >= 3:
                print("Adversary failed 3 times in a row. Aborting.")
                break
            print("Adversay failed to generate a test. Skipping iteration.")
            iteration += 1
            continue
        else:
            consecutive_adversary_failures = 0

        passed = execute_test(current_code, adversarial_tests)
        print(f"Adversarial test {'PASSED' if passed else 'FAILED'}")
        logger.log_iteration(iteration + 1, current_coverage, uncovered_branches, passed)
        all_tests.append(adversarial_tests) #storing adversarial tests irrespective of passed or failed

        if passed:
            consecutive_passes += 1
            print(f"Adversarial test PASSED. Consecutive passes: {consecutive_passes}")
            if consecutive_passes >= 2 and (current_coverage >= coverage_threshold or not with_coverage):
                print(f"Converged: 2 consecutive passes and coverage at {current_coverage}%")
                break
            elif consecutive_passes >= 2:
                print(f"2 consecutive passes but coverage only at {current_coverage}%. Continuing.")
        else:
            consecutive_passes = 0
            current_code = refiner.refine(current_code, adversarial_tests)
            print("Refiner updated the code")

        iteration += 1

    if iteration >= max_iterations:
        print(f"\nReached max iterations ({max_iterations}). Validation incomplete.")
    else:
        print(f"\nValidation complete after {iteration} iteration(s).")
        print(f"Final branch coverage: {current_coverage}%")

    logger.log_final(current_coverage, iteration, final_code=current_code)
    logger.save()

    return current_code

"""
if __name__ == "__main__":
    initial_code = def is_palindrome(s):
    if not isinstance(s, str):
        raise ValueError("Input must be a string")
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    if len(cleaned) == 0:
        return True
    return cleaned == cleaned[::-1]

    model_path = "qwen2.5-coder:7b" #Commands will be: ollama run qwen2.5-coder:7b "prompt"
    result = main(initial_code, model_path, function_name="classify_number", condition="with_coverage", with_coverage=True)

    print("Final validated code:")
    print(result)

"""