from time import time
from os import listdir

from solvepy3 import *

def customTest(tc: Optional[List[int]] = None) -> None:
    print("custom")
    testcases = tc if tc != None else [6, 7, 8, 9]
    for testcase in testcases:
        start = time()
        if testcase == 6:
            print("custom #6:", end=' ')
            print("Correct" if test(f"./testcases/custom/6_SAT.cnf") == True else "Wrong")
        elif testcase == 7:
            print("custom #7:", end=' ')
            print("Correct" if test(f"./testcases/custom/7_UNSAT.cnf") == False else "Wrong")
        elif testcase == 8:
            print("custom #8:", end=' ')
            print("Correct" if test(f"./testcases/custom/8_UNSAT.cnf") == False else "Wrong")
        elif testcase == 9:
            print("custom #9:", end=' ')
            print("Correct" if test(f"./testcases/custom/9_SAT.cnf") == True else "Wrong")
        print(f"elapsed time: {time() - start}s")
    print("------------")

def ufTest(foldername: str, nbtestcases: int, answer: bool, chk: int) -> None:
    print(f"{foldername}, {nbtestcases}")
    fileprefix = foldername.split('-')[0]
    start = time()
    for i in range(1, nbtestcases+1):
        if test(f"./testcases/{foldername}/{fileprefix}-0{i}.cnf") != answer:
            print(f"wrong: {foldername} #{i}")
            exit(0)
        if i % chk == 0:
            print(f"{foldername}: {i / nbtestcases * 100}%")
    print(f"elapsed time: {time() - start}s")
    print("------------")

def miscTest(answer: bool) -> None:
    s = "SAT" if answer else "UNSAT"
    print("misc ", s)
    for filename in listdir(f"./testcases/misc/{s}"):
        start = time()
        print(filename, end=': ')
        print("Correct" if test(f"./testcases/misc/{s}/{filename}") == answer else "Wrong")
        print(f"elapsed time: {time() - start}s")
    print("------------")


if __name__ == '__main__':
    # customTest([6, 7, 8, 9])
    # ufTest("uf20-91", 1000, True, 100)
    # ufTest("uf50-218", 100, True, 10)
    # ufTest("uuf50-218", 100, False, 10)
    # ufTest("uuf250-1065", 100, False, 1)
    miscTest(True)
    miscTest(False)
        