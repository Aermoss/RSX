# R#
An interpreted programming language.
![rsharp logo](./icon.png)

# Getting Started
## How to interprete the program
```
python main.py --interprete main.rsx
```

## How to transpile the program
### Python
```
python main.py --transpile-python main.rsx
```

## How to make a library using python
### library.py
```python
from tools import *

create_library("library")

@create_function("VOID", {"message": "STRING"})
def log(environment):
    print(environment["args"]["message"])

library = pack_library()
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

# Libraries
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
