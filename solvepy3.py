import sys
from typing import List

class Assignment():
    '''
    Assignment = (var, val, isImplied)
    '''
    def __init__(self, var: int, val: bool, isImplied: bool) -> None:
        self.var: int = var
        self.val: bool = val
        self.isImplied: bool = isImplied

class Clause():
    '''
    Clause = (vars, assignedvars, neg, conflict)
    '''
    def __init__(self, vars: List[int], asms: List[Assignment]) -> None:
        self.variableBits: int = 0
        self.remainingBits: int = 0
        self.negativenessBits: int = 0
        self.conflictnessBits: int = 0

        for var in vars:
            if var < 0:
                self.negativenessBits |= (1 << (-var-1))
            self.variableBits |= (1 << (abs(var)-1))
        
        self.remainingBits = self.variableBits
        for asm in asms:
            if self.contains(asm.var):
                varLoc: int = (1 << (asm.var-1))
                self.remainingBits ^= varLoc
                if bool(self.negativeness & varLoc) != asm.val:
                    self.conflictnessBits |= varLoc
    
    def contains(self, var: int) -> bool:
        return bool(self.variableBits & (1 << (var-1)))
    
    def remains(self, var: int) -> bool:
        return bool(self.remainingBits & (1 << (var-1)))
    
    def isUnit(self) -> bool:
        return not (self.remainingBits & (self.remainingBits - 1))

class Formula():
    '''
    Formula = (unit, incomplete, complete, conflict)
    '''
    def __init__(self) -> None:
        self.units: List[Clause] = []
        self.incompletes: List[Clause] = []
        self.completes: List[Clause] = []
        self.conflicts: List[Clause] = []
    
    def addClause(self, clause: Clause) -> None:
        if clause.conflictnessBits:
            self.conflicts.append(clause)
        elif clause.remainingBits == 0:
            self.completes.append(clause)
        elif clause.isUnit():
            self.units.append(clause)
        else:
            self.incompletes.append(clause)


def parse(filename):
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if line.startswith("p cnf"):
                nbvar, nbclauses = map(int, line.split()[2:4])
                break
        
        formula = Formula()
        for i in range(nbclauses):
            clause = Clause(map(int, f.readline().split()[:-1]), [])
            formula.addClause(clause)
    
    return nbvar, nbclauses, formula

def DPLL(nbvar, nbclauses, formula):
    A = list()

    while True:

        while True:
            unit = getUnit(formula)
            if unit is None: break
            assignUnit(unit, A)
        
        if isEmpty(clauses):
            return A
        
        if hasConflict(formula):
            C = learningClause()
            if(isEmpty(C)):
                return None
            
            backtrack(A, C)
            continue
        
        assignNew(A)
        

def main(filename):
    nbvar, nbclauses, formula = parse(filename)
    res = DPLL(nbvar, nbclauses, formula)
    makeOutput(res)

if __name__ == '__main__':
    main(sys.argv[1])