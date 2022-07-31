import sys, os, shutil

sys.dont_write_bytecode = True

def main(argv):
    os.system("python setup.py install --user")
    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.system("python build.py")

    if sys.platform == "win32":
        with open("rsharp.exe", "rb") as file:
            data = file.read()

        shutil.rmtree("rsharp.egg-info")
        os.remove("rsharp.exe")

        if "RSharp" in os.listdir("C:\\"):
            shutil.rmtree("C:\\RSharp")

        os.mkdir("C:\\RSharp")
        shutil.copytree(".\\rsharp\\include", "C:\\RSharp\\include\\")
        shutil.copy(".\\rsharp\\icon.ico", "C:\\RSharp\\")
        shutil.copy(".\\rsharp\\icon.png", "C:\\RSharp\\")
        shutil.copy(".\\rsharp\\icon_alternative.ico", "C:\\RSharp\\")
        shutil.copy(".\\rsharp\\icon_alternative.png", "C:\\RSharp\\")
        shutil.copy(".\\rsharp\\logo.png", "C:\\RSharp\\")
        os.chdir("C:\\RSharp")

        with open("rsharp.exe", "wb") as file:
            file.write(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))