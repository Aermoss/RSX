import sys, os, shutil

sys.dont_write_bytecode = True

def main(argv):
    os.system("python build.py")
    os.system("python setup.py install --user")

    with open("rsharp.exe", "rb") as file:
        data = file.read()

    if "RSharp" in os.listdir("C:\\"):
        shutil.rmtree("C:\\RSharp")

    os.mkdir("C:\\RSharp")
    shutil.copytree(".\\rsharp\\include", "C:\\RSharp\\include")
    os.chdir("C:\\RSharp")

    with open("rsharp.exe", "wb") as file:
        file.write(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))