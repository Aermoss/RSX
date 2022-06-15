include "rsxraylib" : *;
include "rsxmath" : *;
include "rsxstd" : *;

int main() {
    InitWindow(1200, 600, "R#!");

    bool condition() { return std::bnot(WindowShouldClose()); }
    void loop() {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        EndDrawing();
    } std::while_callback("condition", "loop");

    CloseWindow();
    return 0;
}