import sys, os

import rsxpy as rsx

def main(argv):
    tests = {
        "factorial:factorial": {"args": [5], "result": 120},
        "factorial:factorial_alternative": {"args": [5], "result": 120},
        "fibonacci:fibonacci": {"args": [8], "result": 21},
        "fibonacci:fibonacci_alternative": {"args": [8], "result": 21},
        "arrays:arrays_one": {"args": [1, 2], "result": "R#"},
        "arrays:arrays_two": {"args": [4], "result": 400},
        "arrays:arrays_three": {"args": [2], "result": 8},
        "arrays:arrays_four": {"args": [], "result": True},
        "arrays:arrays_five": {"args": [], "result": False},
        "arrays:arrays_six": {"args": [], "result": [1.2, 2.6, 3.1, 4.9]},
        "arrays:arrays_seven": {"args": [[1.2, 2.6, 3.1, 4.9], 2], "result": 3.1},
        "arrays:arrays_eight": {"args": [[0, 1, 2, 3], [4, 5, 6, 7, 8]], "result": [0, 1, 2, 3, 4, 5, 6, 7, 8]},
        "arrays:arrays_nine": {"args": [[0, 1, 2, 3]], "result": 4},
        "arrays:arrays_ten": {"args": [[0, 1, 2, 3]], "result": [3, 2, 1, 0]},
        "arrays:arrays_eleven": {"args": [[0, 1, 2]], "result": [0, 10, 2]},
        "scopes:scopes_one": {"args": [], "result": 8},
        "scopes:scopes_two": {"args": [], "result": 10},
        "variables:variables_one": {"args": [], "result": -30},
        "maths:circle_circumference": {"args": [8], "result": 50.26548245743669},
        "maths:circle_area": {"args": [8], "result": 201.06192982974676},
        "maths:hypotenuse": {"args": [4, 3], "result": 5},
        "keywords:keywords_one": {"args": [], "result": 10},
        "keywords:keywords_two": {"args": [], "result": 10},
        "keywords:keywords_three": {"args": [], "result": 50},
        "keywords:keywords_four": {"args": [], "result": 60},
        "keywords:keywords_five": {"args": [], "result": 70},
        "keywords:keywords_six": {"args": [], "result": 40},
        "functions:functions_one": {"args": [], "result": None},
        "functions:functions_two": {"args": [], "result": 10},
        "functions:functions_three": {"args": [], "result": 20.23},
        "functions:functions_four": {"args": [], "result": "RSX"},
        "functions:functions_five": {"args": [], "result": True},
        # "threads:threads_one": {"args": [], "result": 30},
        "casting:casting_one": {"args": [128], "result": "128"},
    }

    passed, failed = 0, 0
    readed_files = {}

    for i in tests:
        if i.split(":")[0] not in readed_files:
            variables, functions = rsx.tools.extract(file = "tests/" + i.split(":")[0] + ".rsx")
            readed_files[i.split(":")[0]] = {"variables": variables, "functions": functions}

        else:
            functions = readed_files[i.split(":")[0]]["functions"]

        res = "passed" if functions[i.split(":")[1]](*tests[i]["args"]) == tests[i]["result"] else "failed"
        # print(functions[i.split(":")[1]](*tests[i]["args"]))
        print(f"RSX: INFO: running test ", end = "")
        rsx.tools.set_text_attr(14)
        print(i.split(":")[1] + " from " + i.split(":")[0] + ".rsx", end = ": ", flush = True)
        if res == "passed": rsx.tools.set_text_attr(10)
        else: rsx.tools.set_text_attr(12)
        print(res, flush = True)
        rsx.tools.set_text_attr(7)
        if res == "failed": failed += 1
        if res == "passed": passed += 1

    print(f"{passed} passed, {failed} failed out of {len(tests)} tests")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))