#responsible for running adverserial testsagainst the target code


def execute_test(code, test_case):
    try:
        namespace = {"__builtins__":{}} # to store code's variables and functions; builtin prevents the executed code from accessing any built in python functions
        safe_builtins = ["print", "len", "range", "int", "float", "str", "bool", "list", "dict", "tuple", "set", "abs", "max", "min", "sum", "round", "sorted", "enumerate", "zip", "map", "filter", "isinstance", "type", "ValueError", "TypeError", "Exception"]
        namespace["__builtins__"] = {name: __builtins__[name] if isinstance(__builtins__, dict) else getattr(__builtins__, name) for name in safe_builtins if (name in __builtins__ if isinstance(__builtins__, dict) else hasattr(__builtins__, name))}
        exec(code, namespace)
        '''
        --> runs the code string as python code
        --> stores any function or variable defined by it into namespace, to not conflict with our original code
        '''
        func_name = [k for k in namespace if not k.startswith("__") and callable(namespace[k])] #making a list of functions which are not dunder keys and are callable
        func_name = func_name[0] if func_name else None #taking the last callable function name of func_name list otherwise None
        if func_name is None:
            return False
        
        func = namespace[func_name] #getting the actual callable function by using it as key from namespace dict

        test_input = test_case['input']
        expected = test_case['expected']
        
        test_input = test_input if isinstance(test_input, (list, tuple)) else [test_input]
        actual = func(*test_input) #astrick is used for unpacking the list
        '''
        In Python, functions are "first-class objects":
        —they're just values you can store and pass around.'''
        return actual == expected
    except Exception as e:
        print(f"Executor: Test execution failed - {e}")
        return False