# R#
An interpreted statically typed multi paradigm general purpose programming language designed for cross platform applications.
![rsharp logo](rsharp/icon.png)

# Getting Started
## How to interprete the program
```
python main.py main.rsx --interprete
```

## How to transpile the program
### Python
```
python main.py main.rsx --transpile-python
```

## How to make a library using python
### library.py
```python
from tools import *

create_library("library")

@create_function("VOID", {"message": "STRING"})
def log(environment):
    print(environment["args"]["message"], flush = True)

library = pack_library()
```

### main.rsx
```c++
include "library.py";

int main() {
    library::log("Hello, World!");
}
```

## How to make a library using R# header files
### library.rsxh
```c++
include "rsxio" : *;
include "rsxstr" : *;

void log(string message) {
    std::rout(std::addstr(message, "\n"));
}
```

### main.rsx
```c++
include "library.rsxh";

int main() {
    library::log("Hello, World!");
}
```

## How to add an include folder
```
python main.py main.rsx --interprete -Imy-include-folder
```

## How to create the json files for ast and tokens
```
python main.py main.rsx --interprete -ljson
```

# Examples
## Hello, World!
```c++
include "rsxio" : *;

int main() {
    std::rout("Hello, World!\n");
    return 0;
}
```

## Builder
```c++
include "rsxbuild" : *;
include "rsxstr" : *;
include "rsxsys" : *;
include "rsxio" : *;

int main() {
    std::rout("file name > ");
    std::build_program(
        std::rin(),
        std::addstr(std::getdir(), "\\include\\"),
        true, std::addstr(std::getdir(), "\\icon.ico")
    ); return 0;
}
```

# Libraries
- rsxbuild
- rsxthread
- rsxio
- rsxf
- rsxgui
- rsxmath
- rsxmixer
- rsxrand
- rsxraylib
- rsxstr
- rsxstd
- rsxsys
- rsxterm
- rsxtime
- rsxos