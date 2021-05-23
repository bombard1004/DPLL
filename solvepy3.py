import sys
from typing import List, Optional, Tuple
from copy import deepcopy


class Clause():
    '''
    Clause = (vars, assignedvars, neg, conflict)
    '''
    def __init__(self, vars: List[int]) -> None:
        self.variableBits: int = 0
        self.remainingBits: int = 0
        self.positivenessBits: int = 0
        self.satisfiedBits: int = 0

        for var in vars:
            if var > 0:
                self.positivenessBits |= (1 << (var-1))
            self.variableBits |= (1 << (abs(var)-1))
        
        self.remainingBits = self.variableBits
    
    def contains(self, varLoc: int) -> bool:
        return bool(self.variableBits & varLoc)
    
    def remains(self, varLoc: int) -> bool:
        return bool(self.remainingBits & varLoc)
    
    def isUnit(self) -> bool:
        return not (self.remainingBits & (self.remainingBits - 1))
    
    def empty(self) -> bool:
        return self.variableBits == 0
    
    def assign(self, varLoc: int, val: bool) -> None:
        if self.contains(varLoc):
            self.remainingBits ^= varLoc
            if bool(varLoc & self.positivenessBits) == val:
                self.satisfiedBits |= varLoc
    
    def cancel(self, varLoc: int, val: bool) -> None:
        if self.contains(varLoc):
            self.remainingBits ^= varLoc
            self.satisfiedBits &= (~varLoc)
    
    def assignMulti(self, varLocs: int, vals: int) -> None:
        self.satisfiedBits |= ((self.remainingBits & varLocs) & (~(self.positivenessBits ^ vals)))
        self.remainingBits &= (~varLocs)

class Assignment():
    '''
    Assignment = (var, val, impliedClause)
    '''
    def __init__(self, varLoc: int, val: bool, impliedClause: Optional[Clause]) -> None:
        self.varLoc: int = varLoc
        self.val: bool = val
        self.impliedClause: Optional[Clause] = impliedClause

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
        if clause.satisfiedBits:
            self.completes.append(clause)
        elif clause.remainingBits == 0:
            self.conflicts.append(clause)
        elif clause.isUnit():
            self.units.append(clause)
        else:
            self.incompletes.append(clause)
    
    def hasUnit(self) -> bool:
        return len(self.units) > 0
    
    def noClauses(self) -> bool:
        return len(self.units) == 0 and len(self.incompletes) == 0 and len(self.conflicts) == 0
    
    def hasConflict(self) -> bool:
        return len(self.conflicts) > 0
    
    def assignAll(self, varLoc: int, val: bool) -> None:
        for c in self.units:
            c.assign(varLoc, val)
        for c in self.incompletes:
            c.assign(varLoc, val)
        for c in self.completes:
            c.assign(varLoc, val)

        self.rearrange(afterAssign=True)
    
    def assignAllMulti(self, varLocs: int, vals: int) -> None:
        for c in self.units:
            c.assignMulti(varLocs, vals)
        for c in self.incompletes:
            c.assignMulti(varLocs, vals)
        for c in self.completes:
            c.assignMulti(varLocs, vals)
        
        self.rearrange(afterAssign=True)
          
    def rearrange(self, afterAssign: bool) -> None:
        if afterAssign:
            # units -> units, completes, conflicts
            # incompletes -> units, incompletes, completes
            # completes -> completes (no need to rearrange)
            # conflicts -> conflicts (no need to rearrange)
            # order: units => incompletes
            prevUnits = self.units[:]
            self.units.clear()
            for c in prevUnits:
                self.addClause(c)
            
            prevIncompletes = self.incompletes[:]
            self.incompletes.clear()
            for c in prevIncompletes:
                self.addClause(c)
        
        else:
            # units -> units, incompletes
            # incompletes -> incompletes (no need to rearrange)
            # completes -> units, incompletes, completes
            # conflicts -> units, incompletes, conflicts
            # order: units => completes => conflicts (units => conflicts => completes also OK)
            prevUnits = self.units[:]
            self.units.clear()
            for c in prevUnits:
                self.addClause(c)
            
            prevCompletes = self.completes[:]
            self.completes.clear()
            for c in prevCompletes:
                self.addClause(c)
            
            prevConflicts = self.conflicts[:]
            self.conflicts.clear()
            for c in prevConflicts:
                self.addClause(c)

def parse(filename: str) -> Tuple[int, int, Formula]:
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if line.startswith("p cnf"):
                nbvar, nbclauses = map(int, line.split()[2:4])
                break
        
        formula = Formula()
        for _ in range(nbclauses):
            clause = Clause(map(int, f.readline().split()[:-1]))
            formula.addClause(clause)
    
    return nbvar, nbclauses, formula

def assignNew(A: List[Assignment], formula: Formula, nbvar: int) -> None:
    bits = (1 << nbvar) - 1
    for asm in A:
        bits ^= asm.varLoc
    
    varLoc = (bits & -bits)

    formula.assignAll(varLoc, True)
    A.append(Assignment(varLoc, True, None))

def learningClause(A: List[Assignment], conf: Clause) -> Clause:
    D = deepcopy(conf)
    for asm in reversed(A):
        if asm.impliedClause != None and D.contains(asm.varLoc):
            C = asm.impliedClause
            resolveLoc = (D.variableBits & C.variableBits) & (D.positivenessBits ^ C.positivenessBits)
            D.variableBits = (D.variableBits | C.variableBits) ^ resolveLoc
            D.positivenessBits = (D.positivenessBits | C.positivenessBits) ^ resolveLoc

    D.satisfiedBits = 0
    D.remainingBits = 0
    return D

def backtrack(A: List[Assignment], C: Clause, formula: Formula) -> None:
    while True:
        asm = A.pop()
        for c in formula.units:
            c.cancel(asm.varLoc, asm.val)
        for c in formula.incompletes:
            c.cancel(asm.varLoc, asm.val)
        for c in formula.completes:
            c.cancel(asm.varLoc, asm.val)
        for c in formula.conflicts:
            c.cancel(asm.varLoc, asm.val)
        C.cancel(asm.varLoc, asm.val)

        if C.remainingBits:
            break
    
    formula.rearrange(afterAssign=False)
    formula.addClause(C)

def DPLL(nbvar: int, nbclauses: int, formula: Formula) -> Optional[List[Assignment]]:
    A: List[Assignment] = []
    while True:

        while formula.hasUnit():
            units = formula.units[:]
            varLocs = 0
            vals = 0

            for unit in units:
                varLoc = unit.remainingBits
                val = varLoc & unit.positivenessBits
                if (varLocs & varLoc) == 0:
                    varLocs |= varLoc
                    vals |= val
                    A.append(Assignment(varLoc, bool(val), unit))
            
            formula.assignAllMulti(varLocs, vals)
        
        if formula.noClauses():
            return A
        
        if formula.hasConflict():
            C: Clause = learningClause(A, formula.conflicts[0])
            if(C.empty()):
                return None
            
            backtrack(A, C, formula)
            continue
        
        assignNew(A, formula, nbvar)
        

def main(filename: str) -> None:
    nbvar, nbclauses, formula = parse(filename)
    res = DPLL(nbvar, nbclauses, formula)
    print("UNSAT" if res == None else "SAT")

def test(filename: str) -> bool:
    nbvar, nbclauses, formula = parse(filename)
    res = DPLL(nbvar, nbclauses, formula)
    return res != None

if __name__ == '__main__':
    main(sys.argv[1])