#!/usr/bin/env python3

"""
sample inputs:
in/*

sample outputs:
out/*

how to run:
./Main.py <file>.py

"""

# Source - https://stackoverflow.com/a/287944
# Posted by joeld, modified by community. See post 'Timeline' for change history
# Retrieved 2026-10-05, License - CC BY-SA 4.0
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


import subprocess, argparse, os, time

parser = argparse.ArgumentParser(description="Kattis tester script.")
parser.add_argument("filename", type=str, help="The name of the file to test")
parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
parser.add_argument("-c", "--case", type=str, help="Specify specific case to run")
parser.add_argument("-t", "--limit", type=float, help="Time limit (in seconds) for grading.")
parser.add_argument("-b", "--bypass", action="store_true", help="Bypass the Time Limit Exceeded (TLE) constraint.")


args = parser.parse_args()
verbose = args.verbose
case_to_run = args.case
time_limit:float = args.limit
bypass_tle:bool = args.bypass

if not time_limit:
    time_limit = 1.0

def log(inp:str) -> None:
    if verbose:
        print(inp)



def auto_detect_files() -> list[str]:
    if not os.path.exists(IN_PATH) or not os.path.exists(OUT_PATH): 
        print("Input directory or sample output directory doesn't exist!")
        exit(1)
    else:
        try:
            in_case:list[str] = [f for f in os.listdir(IN_PATH)]
            out_case:list[str] = [f for f in os.listdir(OUT_PATH)]

            cases:list[str] = []
            for file in in_case:
                if file in out_case:
                    cases.append(file)
                    log(f"Pair detected: {file}")
                else:
                    log(f"Input detected, but no output pair found: {file}")
            return cases

        except Exception as e:
            print("Error", f"Could not read folders: {e}")
            exit(1)




program:str = args.filename
main_path:str = os.path.dirname(os.path.realpath(program))

log(f"Program directory: {main_path}")

IN_PATH:str = f"{main_path}/in"
OUT_PATH:str = f"{main_path}/out"

log(f"Case inputs directory: {IN_PATH}")
log(f"Case inputs directory: {OUT_PATH}")

cases:list[str] = auto_detect_files()

if len(cases) == 0:
    print("No case pairs found, make sure file names align.\ni.e.: in/0.txt\tout/0.txt")
else:
    print(f"Cases detected: {len(cases)}")


if case_to_run:
    if case_to_run in cases:
        cases.clear()
        cases.append(case_to_run)
    else:
        print(f"Specified case {case_to_run} not found!")
        exit(1)


results:list[str] = []
errors:list[str] = []
codes:list[int] = []
passed:list[bool] = []
time_elapsed:list[float] = []

for case in cases:
    in_file:str = f"{IN_PATH}/{case}"
    out_file:str = f"{OUT_PATH}/{case}"

    start_time:float = time.time()

    try:
        with open(in_file, "r") as f: 
            result_process = subprocess.run(
                ["python", program],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=None if bypass_tle else time_limit
            )

        end_time:float = time.time()
        delta_time = end_time - start_time
        time_elapsed.append(delta_time)

        result: str = result_process.stdout
        error_result: str = result_process.stderr

        log(f"-----\nOutput for case {case}:\n{result}\n-----")
        log(f"-----\nError output for case {case}:\n{error_result}\n-----")


        result = result.strip()

        log(f'Stripped output:\n{result}\n-----')

        error_result = error_result.strip()


        results.append(result)
        errors.append(error_result)
        codes.append(result_process.returncode)

        with open(out_file, "r") as f:
            passed.append((f.read().strip() == result))

    except subprocess.TimeoutExpired:
        end_time = time.time() # type: ignore
        delta_time = end_time - start_time
        time_elapsed.append(delta_time)

        error_result = f"Subprocess killed: Time limit of {time_limit}s exceeded."
        log(f"-----\nError output for case {case}:\n{error_result}\n-----")

        results.append("")
        errors.append(error_result)
        codes.append(124)  # 124 is a standard exit code for timeout
        passed.append(False)

for i, case in enumerate(cases):
    if codes[i] != 0:
        print(f"\n----- EXIT CODE {codes[i]} - {case} -----")
        print(errors[i])
        print("-------------------")
        continue

    if not passed[i]:
        print(f"\n----- FAIL {case} -----")

        out_file = f"{OUT_PATH}/{case}"
        with open(out_file, "r") as f:
            expected:str = f.read()
        got:str = results[i]

        print("== Expected ==")
        print(f"{expected}")
        print("== Got ==")
        print(f"{got}")
        print("-------------------")



# print results
print("\n-------------------- RESULTS ---------------------")

# Find the longest case name for dynamic padding (minimum width of 10)
max_case_len = max([len(c) for c in cases]) if cases else 10

for i, case in enumerate(cases):
    # Print the case name, left-aligned to the max case length
    print(f"| {case:<{max_case_len}} :", end="  ")

    # Determine status text and apply fixed-width padding INSIDE the color tags 
    # to avoid ANSI escape codes messing up the string length calculation
    if not bypass_tle and time_elapsed[i] >= time_limit:
        print(f"{bcolors.FAIL}{'TIME EXCEEDED':<13}{bcolors.ENDC}", end=" | ")
    elif passed[i]:
        print(f"{bcolors.OKGREEN}{'PASSED':<13}{bcolors.ENDC}", end=" | ")
    elif codes[i] != 0:
        # Truncate exit code string if it's bizarrely long, but usually it's just "EXIT CODE X"
        exit_str = f"EXIT CODE {codes[i]}"
        print(f"{bcolors.FAIL}{exit_str:<13}{bcolors.ENDC}", end=" | ")
    else:
        print(f"{bcolors.FAIL}{'FAILED':<13}{bcolors.ENDC}", end=" | ")

    # Right-align the time for a clean decimal line-up
    if time_elapsed[i] > time_limit:
        print(f"{bcolors.FAIL}{time_elapsed[i]:>6.3f}s{bcolors.ENDC}")
    elif time_elapsed[i] < (time_limit/2):
        print(f"{time_elapsed[i]:>6.3f}s")
    else:
        print(f"{bcolors.WARNING}{time_elapsed[i]:>6.3f}s{bcolors.ENDC}")

passed_count: int = sum(1 for p in passed if p)
success_count: int = sum(1 for c in codes if c == 0)
time_conforming_count: int = sum(1 for t in time_elapsed if bypass_tle or t < time_limit)

print(f"---- {success_count}/{len(passed)} RAN ---- {passed_count}/{len(passed)} PASSED ---- {time_conforming_count}/{len(passed)} IN TIME ----")

if success_count != len(passed):
    exit(1)
if passed_count != len(passed):
    exit(1)
if time_conforming_count != len(passed):
    exit(1)