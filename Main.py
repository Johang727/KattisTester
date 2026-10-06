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


args = parser.parse_args()
verbose = args.verbose
case_to_run = args.case
time_limit:float = args.limit

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

    with open(in_file, "r") as f: 
        result_process = subprocess.run(
            ["python", program],
            stdin=f,
            capture_output=True,
            text=True,
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
for i, case in enumerate(cases):
    #print(f"| Case {case}: {f"{bcolors.OKGREEN}PASSED{bcolors.ENDC}" if passed[i] else ("FAILED" if (codes[i] == 0) else f"EXIT CODE {codes[i]}")} - {time_elapsed[i]:.3f}s")

    print(f"| Case {case}:", end="  ")

    if time_elapsed[i] >= time_limit:
        print(f"{bcolors.FAIL}TIME EXCEEDED{bcolors.ENDC}", end=" ")
    elif passed[i]:
        print(f"{bcolors.OKGREEN}PASSED{bcolors.ENDC}", end=" ")
    elif codes[i] != 0:
        print(f"{bcolors.FAIL}EXIT CODE {codes[i]}{bcolors.ENDC}", end=" ")
    else:
        print(f"{bcolors.FAIL}FAILED{bcolors.ENDC}", end=" ")

    print(f"- {time_elapsed[i]:.3f}s")

passed_count: int = 0

for pass_bool in passed:
    if pass_bool:
        passed_count += 1

success_count:int = 0
for code in codes:
    if code == 0:
        success_count += 1

time_conforming_count: int = 0
for tiempo in time_elapsed:
    if tiempo < time_limit:
        time_conforming_count += 1


print(f"---- {success_count}/{len(passed)} RAN ---- {passed_count}/{len(passed)} PASSED ---- {time_conforming_count}/{len(passed)} IN TIME ----")

if success_count != len(passed):
    exit(1)
if passed_count != len(passed):
    exit(1)
if time_conforming_count != len(passed):
    exit(1)