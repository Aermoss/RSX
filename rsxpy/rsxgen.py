import sys, os

try:
    import rsxpy.core as core
    import rsxpy.tools as tools
    import rsxpy.std as std
    import rsxpy.builder as builder
    import rsxpy.preprocessor as preprocessor

except ImportError:
    sys.path.append(os.path.split(os.getcwd())[0])

    import rsxpy.core as core
    import rsxpy.tools as tools
    import rsxpy.std as std
    import rsxpy.builder as builder
    import rsxpy.preprocessor as preprocessor

class Module:
    def __init__(self, name):
        self.name = name
        self.child = None
        self.functions = []
        self.ast = []

    def include(self, name, namespace):
        self.ast.append({"type": "include", "all": not namespace, "value": name})

    def get(self):
        tmp = self.ast.copy()

        for i in self.functions:
            tmp.append(i.get())

        return tmp

class ASTBuilder:
    def __init__(self, parent):
        self.parent = parent
        self.parent.child = self

    def add(self, a, b, get = True):
        ast = {"type": "add", "left": a, "right": b}
        if get: return ast
        else: self.parent.ast.append(ast)

    def sub(self, a, b, get = True):
        ast = {"type": "sub", "left": a, "right": b}
        if get: return ast
        else: self.parent.ast.append(ast)

    def div(self, a, b, get = True):
        ast = {"type": "div", "left": a, "right": b}
        if get: return ast
        else: self.parent.ast.append(ast)

    def mul(self, a, b, get = True):
        ast = {"type": "mul", "left": a, "right": b}
        if get: return ast
        else: self.parent.ast.append(ast)

    def mod(self, a, b, get = True):
        ast = {"type": "mod", "left": a, "right": b}
        if get: return ast
        else: self.parent.ast.append(ast)

    def ret(self, value, get = False):
        ast = {"type": "return", "value": value}
        if get: return ast
        else: self.parent.ast.append(ast)

    def call(self, name, args, get = False):
        ast = {"type": "call", "name": name, "args": args}
        if get: return ast
        else: self.parent.ast.append(ast)

    def get(self):
        return self.parent.get()

class Function:
    def __init__(self, module, type: tools.FunctionType, name: str):
        self.module = module
        self.module.functions.append(self)
        self.child = None
        self.type = type
        self.name = name
        self.ast = []

    def get(self):
        return {"type": "func", "return_type": self.type.return_type, "args": self.type.args, "name": self.name, "ast": self.ast}