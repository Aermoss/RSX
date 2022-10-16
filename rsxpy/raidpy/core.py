import os, sys, configparser, subprocess

try:
    import rsxpy.tools as tools
    import rsxpy.core as core

except ImportError:
    sys.path.append(os.path.split(os.path.split(os.getcwd())[0])[0])

    import rsxpy.tools as tools
    import rsxpy.core as core

def error(message, type = "error", terminated = False):
    print(f"raid:", end = " ", flush = True)
    tools.set_text_attr(12)
    print(f"{type}:", end = " ", flush = True)
    tools.set_text_attr(7)
    print(message, end = "\n", flush = True)
    if terminated: print("program terminated.")
    sys.exit(-1)

console_sample = """include "rsxio" : *;

int main(string[] args) {
    std::rout("Hello, World!" + std::endl());
    return 0;
}"""

raylib_sample = """include "rsxraylib" : *;

int main(string[] args) {
    InitWindow(1200, 600, "R#");
    // SetTargetFPS(60);

    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        DrawFPS(10, 10);
        EndDrawing();
    }

    CloseWindow();
    return 0;
}"""

web_server_sample = """include "rsxsocket", "rsxio" : *;

int main(string[] args) {
    auto server = std::socket(std::AF_INET, std::SOCK_STREAM);
    std::bind(server, "localhost", 5656);
    std::listen(server);

    string index = "HTTP/1.1 200 OK\n\n<p>Hello, World!</p>";

    while (true) {
        auto connection = std::accept(server);
        string response = std::recv(connection, 1024);
        std::rout(response + std::endl());
        std::send(connection, index);
        std::close(connection);
    }
    
    return 0;
}"""

help = """
- help: for this page
- version: for the version of raid
- new [type] [name] [args]: for creating a new project
- run [args]: for running the project in this directory
- run [project] [args]: for running a project
- build [args]: for building the project in this directory
- build [project] [args]: for building a project

project for run/build commands: project name (example: my_project)
args for run/build commands: same as R# commands (example: -timeit=true)
args for new command: [key]=[value] changes the values in rsxconfig.ini (example: method=rsx)
type for new command: [console/raylib/web_server] (example: console)
"""

def main():
    argv = sys.argv
    version = "0.0.1"

    include_folders = ["./", "../include"]
    if sys.platform == "win32" and tools.is_compiled(): include_folders.append("C:\\RSX\\include\\")

    samples = {
        "console": console_sample,
        "raylib": raylib_sample,
        "web_server": web_server_sample
    }

    if len(argv) == 1:
        print(help)
        return 0

    if argv[1] == "new":
        if argv[2] not in samples:
            error("please select a application type (write 'help' for more information)")

        if argv[3] in os.listdir():
            error("file already exists")

        os.mkdir(argv[3])
        os.chdir(argv[3])
        os.mkdir("src")
        os.mkdir("build")
        os.mkdir("include")

        config = configparser.ConfigParser()
        config["settings"] = {
            "project": argv[3],
            "version": "0.0.1",
            "author": "unknown",
            "include_folders": ",".join(include_folders),
            "rsx-version": tools.get_version(),
            "raid-version": version,
            "method": "rsxpy" if not tools.is_compiled() else "rsx",
            "entry": "main.rsx"
        }

        for i in argv[4:]:
            config["settings"][i.split("=")[0]] = i.split("=")[1]

        with open("rsxconfig.ini", "w") as file:
            config.write(file)

        code = ("raid" if tools.is_compiled() else "raidpy") + " run"

        with open("run.bat", "w") as file:
            file.write(code)

        with open("run.sh", "w") as file:
            file.write("#!/bin/sh" + "\n" + code)

        os.chdir("src")
        
        with open("main.rsx", "w") as file:
            file.write(samples[argv[2]])

    elif argv[1] == "help":
        print(help)

    elif argv[1] == "version":
        tools.set_text_attr(12)
        print(f"Raid {version}", flush = True)
        tools.set_text_attr(7)

    elif argv[1] in ["run", "build"]:
        if len(argv) > 2:
            os.chdir(argv[2])
            argv.pop(2)

        if "rsxconfig.ini" not in os.listdir():
            error("couldn't find any project")

        config = configparser.ConfigParser()
        config.read("rsxconfig.ini")

        if config["settings"]["rsx-version"] != tools.get_version() and config["settings"]["method"] == "rsxpy":
            error("R# version mismatch")

        if config["settings"]["raid-version"] != version:
            error("Raid version mismatch")

        include_folders = []

        for i in config["settings"]["include_folders"].split(","):
            include_folders.append(f"-I{i}")

        os.chdir("src")
        subprocess.run([config["settings"]["method"], argv[1], config["settings"]["entry"]] + include_folders + argv[2:])

        if argv[1] == "build":
            with open(os.path.splitext(config["settings"]["entry"])[0] + ".exe", "rb") as file:
                data = file.read()

            os.remove(os.path.splitext(config["settings"]["entry"])[0] + ".exe")
            os.chdir("../build")

            with open(os.path.splitext(config["settings"]["entry"])[0] + ".exe", "wb") as file:
                file.write(data)

    else:
        error("no operation")

    return 0

if __name__ == "__main__":
    sys.exit(main())