import sys

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

def main(filename):
    nbvar, nbclauses, clauses = parse(filename)
    for clause in clauses:
        print(clause)

if __name__ == '__main__':
    main(sys.argv[1])