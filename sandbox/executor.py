#responsible for running adverserial testsagainst the target code

import sys #gives access to redirect stdout
from io import StringIO #creates an in-memory text stream to capture print statements

def execute_test(code, test_case):
    try:
        namespace = {} # to store code's variables and functions
        exec(code, namespace)
        '''
        --> runs the code string as python code
        --> stores any function or variable defined by it into namespace, to not conflict with our original code'''
        func_name = list(namespace.keys())[-1] #assuming LLM generated code contains only one function
        func = namespace[func_name] #getting the actual callable function by using it as key from namespace dict

        test_input = test_case['input']
        expected = test_case['expected']
        
        actual = func(test_input)
        '''
        In Python, functions are "first-class objects":
        —they're just values you can store and pass around.'''
        return actual == expected
    except Exception as e:
        print(f"Executor: Test execution failed - {e}")
        return False