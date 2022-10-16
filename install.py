import sys, os, shutil, importlib

sys.dont_write_bytecode = True

def main(argv):
    os.system("python setup.py install --user")
    shutil.rmtree("rsxpy.egg-info")

    for i in os.listdir("rsxpy/include"):
        print(f"RSX: INFO: byte-compiling: {i}")
        rsxpy = importlib.import_module("rsxpy")
        context = rsxpy.core.Context([], "<build>")
        context.include_folders = ["rsxpy/include"]
        rsxpy.tools.include_library(context, [i], False, None, None)

    shutil.rmtree("build", ignore_errors = True)
    shutil.rmtree("dist", ignore_errors = True)
    os.system("python build.py")

    if sys.platform == "win32":
        if "RSX" in os.listdir("C:\\"):
            shutil.rmtree("C:\\RSX")

        os.mkdir("C:\\RSX")
        shutil.copytree(".\\rsx", "C:\\RSX", dirs_exist_ok = True)
        shutil.copytree(".\\raid", "C:\\RSX", dirs_exist_ok = True)
        shutil.rmtree(".\\rsx", ignore_errors = True)
        shutil.rmtree(".\\raid", ignore_errors = True)
        shutil.copytree(".\\rsxpy\\include", "C:\\RSX\\include")
        shutil.copy(".\\rsxpy\\raidpy\\raid_logo.png", "C:\\RSX\\")
        shutil.copy(".\\rsxpy\\raidpy\\raid_icon.ico", "C:\\RSX\\")
        shutil.copy(".\\rsxpy\\icon.ico", "C:\\RSX\\")
        shutil.copy(".\\rsxpy\\icon.png", "C:\\RSX\\")
        shutil.copy(".\\rsxpy\\icon_alternative.ico", "C:\\RSX\\")
        shutil.copy(".\\rsxpy\\icon_alternative.png", "C:\\RSX\\")
        shutil.copy(".\\rsxpy\\logo.png", "C:\\RSX\\")
        os.chdir("C:\\RSX")

if __name__ == "__main__":
    sys.exit(main(sys.argv))