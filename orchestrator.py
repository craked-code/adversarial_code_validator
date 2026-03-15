#entry point that imports from agent and sandbox

from agents.generator import Generator
from agents.adversary import Adversary
from agents.refiner import Refiner
from sandbox.executor import execute_test

def main(initial_code, model_path, max_iterations=10):
    #intantiating
    generator = Generator(model_path)
    adversary = Adversary(model_path)
    refiner = Refiner(model_path)

    current_code = initial_code
    all_tests = [] #to collect every test generated across all iterations
    iteration = 0
    consecutive_generator_faliures = 0
    consecutive_adversary_faliures = 0

    while iteration < max_iterations:
        print(f"\n-- Iteration {iteration + 1} --")
        tests = generator.generate(current_code)
        if not tests:
            consecutive_generator_faliures += 1 
            if consecutive_generator_faliures >=3:
                print("Generator failed 3 times in a row. Aborting.")
                break
            iteration += 1
            continue
        else: 
            consecutive_generator_faliures = 0
        
        print(f"Generator produced {len(tests)} test(s)")
        all_tests.extend(tests) #we use extend instead of append because test is already a list
        '''
        we do not need to keep track of which test was generated at which iteration
        the goal of all_tests is to answer one question during convergence — 
        "does the current code pass every test we have ever seen?"
        '''

        adverserial_tests = adversary.attack(current_code, tests)
        if adverserial_tests is None:
            consecutive_adversary_faliures += 1
            if consecutive_adversary_faliures >= 3:
                print("Adversary failed 3 times in a row. Aborting.")
                break
            print("Adversay failed to generate a test. Skipping iteration.")
            iteration += 1
            continue
        else:
            consecutive_adversary_faliures = 0

        passed = execute_test(current_code, adverserial_tests)
        print(f"Adversarial test {'PASSED' if passed else 'FAILED'}")
        all_tests.append(adverserial_tests) #storing adverserial tests irrespective of passed or failed

        if passed:
            break
        current_code = refiner.refine(current_code, adverserial_tests)
        print("Refiner updated the code")
        iteration += 1

    if iteration >= max_iterations:
        print(f"\nReached max iterations ({max_iterations}). Validation incomplete.")
    else:
        print(f"\nValidation complete after {iteration + 1} iteration(s).")
        
    return current_code


if __name__ == "__main__":
    initial_code = """def add(a, b):
                        return a+b
    """
    model_path = "qwen2.5-coder:7b" #Commands will be: ollama run qwen2.5-coder:7b "prompt"
    result = main(initial_code, model_path)

    print("Final validated code:")
    print(result)