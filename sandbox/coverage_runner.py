import coverage
import tempfile
import os
import importlib.util
import time

def get_coverage(code, test_cases):
    if not test_cases:
        return 0.0, "No tests available"
    
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_path = f.name
            f.write(code)

        cov = coverage.Coverage(branch=True, data_file=None)
        cov.start()

        for test_case in test_cases:
            try:
                spec = importlib.util.spec_from_file_location(f'temp_module_{time.time_ns()}', temp_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                func_name = [k for k in dir(mod) if not k.startswith('__') and callable(getattr(mod, k))]
                func_name = func_name[0] if func_name else None
                if func_name:
                    func = getattr(mod, func_name)
                    test_input = test_case['input']
                    test_input = test_input if isinstance(test_input, (list, tuple)) else [test_input]
                    func(*test_input)
            except Exception:
                pass

        cov.stop()
        cov.save()

        measured = cov.get_data().measured_files()
        if not measured:
            os.unlink(temp_path)
            return 0.0, "No coverage data collected"

        target = [f for f in measured if os.path.basename(temp_path) in os.path.basename(f)]
        if not target:
            os.unlink(temp_path)
            return 0.0, "Could not match temp file in coverage data"
        target = target[0]
        
        analysis_obj = cov._analyze(target)
        numbers = analysis_obj.numbers

        covered_branches = numbers.n_branches - numbers.n_missing_branches
        total_branches = numbers.n_branches
        coverage_pct = (covered_branches / total_branches * 100) if total_branches > 0 else 100.0

        missing_arcs = analysis_obj.missing_branch_arcs()
        descriptions = []
        for from_line, to_lines in missing_arcs.items():
            for to_line in to_lines:
                descriptions.append(f"line {from_line} branch to line {to_line} never taken")

        uncovered_str = ", ".join(descriptions) if descriptions else "All branches covered"

        os.unlink(temp_path)
        return round(coverage_pct, 2), uncovered_str

    except Exception as e:
        try:
            os.unlink(temp_path)
        except:
            pass
        return 0.0, f"Coverage analysis failed: {str(e)}"