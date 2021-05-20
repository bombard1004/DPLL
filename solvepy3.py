import sys

# clause = (vars, assignedvars, neg, conflict)
# cluases = (unit, incomplete, complete, conflict)

def parse(filename):
    with open(filename, 'r') as f:
        while True:
            line = f.readline()
            if line.startswith("p cnf"):
                nbvar, nbclauses = map(int, line.split()[2:4])
                break
        
        clauses = list()
        for i in range(nbclauses):
            clause = [0] * nbvar
            for var in map(int, f.readline().split()[:-1]):
                clause[abs(var)-1] = 1 if var > 0 else -1
            clauses.append(clause)
    
    return nbvar, nbclauses, clauses

def DPLL(nbvar, nbclauses, clauses):
    A = list()

    while True:

        while True:
            unit = getUnit(clauses)
            if unit is None: break
            assignUnit(unit, A)
        
        if isEmpty(clauses):
            return A
        
        if hasConflict(clauses):
            C = learningClause()
            if(isEmpty(C)):
                return None
            
            backtrack(A, C)
            continue
        
        assignNew(A)
        

def main(filename):
    nbvar, nbclauses, clauses = parse(filename)
    res = DPLL(nbvar, nbclauses, clauses)
    makeOutput(res)

if __name__ == '__main__':
    main(sys.argv[1])