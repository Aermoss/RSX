import sys, rsxpy

def main(argv):
    rsxpy.tools.recompile_libs()

if __name__ == "__main__":
    sys.exit(main(sys.argv))