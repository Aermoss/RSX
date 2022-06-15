from rsharp.main import *

code = """include "rsxraylib" : *;
include "rsxtime" : *;
include "rsxstd" : *;
include "rsxmath" : *;

int main() {
    InitWindow(1200, 600, "Aermoss");

    bool condition() { return std::bnot(WindowShouldClose()); }
    void loop() {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        EndDrawing();
    } std::while_callback("condition", "loop");

    CloseWindow();
    return 0;
}"""

variables = {}
functions = {}
library_functions = {}
create_json = False
name = "test.rsx"
include_folders = ["rsharp/include"]

interpreter(parser(lexer(code, name, create_json), name, create_json), name, True, False, functions, variables, None, library_functions, include_folders, create_json)