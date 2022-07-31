include "rsxbuild" : *;
include "rsxsys" : *;
include "rsxio" : *;

int main() {
    std::rout("file name > ");
    std::build_program(
        std::rin(),
        std::getdir() + "/include/",
        true, std::getdir() + "/icon.ico"
    ); return 0;
}