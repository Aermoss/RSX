include "rsxbuild" : *;
include "rsxstr" : *;
include "rsxsys" : *;
include "rsxio" : *;

int main() {
    std::rout("file path > ");
    std::build_program(
        std::rin(),
        std::addstr(std::getdir(), "\\include\\"),
        true, std::addstr(std::getdir(), "\\icon.ico")
    ); return 0;
}