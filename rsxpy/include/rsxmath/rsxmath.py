from rsxpy.tools import *

import math

create_library("rsxmath")

@create_function("INT", {"a": "INT", "b": "INT"})
def add(environment):
    return environment["args"]["a"] + environment["args"]["b"]

@create_function("INT", {"a": "INT", "b": "INT"})
def sub(environment):
    return environment["args"]["a"] - environment["args"]["b"]

@create_function("INT", {"a": "INT", "b": "INT"})
def mul(environment):
    return environment["args"]["a"] * environment["args"]["b"]

@create_function("INT", {"a": "INT", "b": "INT"})
def div(environment):
    return int(environment["args"]["a"] / environment["args"]["b"])

@create_function("INT", {"a": "INT", "b": "INT"})
def pow(environment):
    return environment["args"]["a"] ** environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def addf(environment):
    return environment["args"]["a"] + environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def subf(environment):
    return environment["args"]["a"] - environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def mulf(environment):
    return environment["args"]["a"] * environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def divf(environment):
    return environment["args"]["a"] / environment["args"]["b"]

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def powf(environment):
    return environment["args"]["a"] ** environment["args"]["b"]

@create_function("INT", {"a": "FLOAT", "b": "FLOAT"})
def gcd(environment):
    return math.gcd(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def fmod(environment):
    return math.fmod(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def hypot(environment):
    return math.hypot(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT"})
def gamma(environment):
    return math.gamma(environment["args"]["a"])

@create_function("BOOL", {"a": "FLOAT"})
def isinf(environment):
    return math.isinf(environment["args"]["a"])

@create_function("BOOL", {"a": "FLOAT"})
def isfinite(environment):
    return math.isfinite(environment["args"]["a"])

@create_function("BOOL", {"a": "FLOAT"})
def isnan(environment):
    return math.isnan(environment["args"]["a"])

@create_function("INT", {"a": "FLOAT"})
def isqrt(environment):
    return math.isqrt(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT", "b": "INT"})
def ldexp(environment):
    return math.ldexp(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT"})
def lgamma(environment):
    return math.lgamma(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def log(environment):
    return math.log(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT"})
def log10(environment):
    return math.log10(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def log1p(environment):
    return math.log1p(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def log2(environment):
    return math.log2(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def fsum(environment):
    return math.fsum(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT"})
def degrees(environment):
    return math.degrees(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def radians(environment):
    return math.radians(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def cos(environment):
    return math.cos(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def cosh(environment):
    return math.cosh(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def cbrt(environment):
    return math.cbrt(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def erf(environment):
    return math.erf(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def erfc(environment):
    return math.erfc(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def exp(environment):
    return math.exp(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def exp2(environment):
    return math.exp(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def expm1(environment):
    return math.expm1(environment["args"]["a"])

@create_function("INT", {"a": "INT"})
def factorial(environment):
    return math.factorial(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def fabs(environment):
    return math.fabs(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def copysign(environment):
    return math.copysign(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def dist(environment):
    return math.dist(environment["args"]["a"], environment["args"]["b"])

@create_function("INT", {"a": "FLOAT", "b": "FLOAT"})
def comb(environment):
    return math.comb(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT"})
def sin(environment):
    return math.sin(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def sinh(environment):
    return math.sinh(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def tan(environment):
    return math.tan(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def tanh(environment):
    return math.tanh(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def sqrt(environment):
    return math.sqrt(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def ulp(environment):
    return math.ulp(environment["args"]["a"])

@create_function("INT", {"a": "FLOAT"})
def trunc(environment):
    return math.trunc(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def remainder(environment):
    return math.remainder(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def atan(environment):
    return math.atan(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def atan2(environment):
    return math.atan2(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT", "b": "FLOAT"})
def nextafter(environment):
    return math.atan2(environment["args"]["a"], environment["args"]["b"])

@create_function("INT", {"a": "FLOAT", "b": "FLOAT"})
def perm(environment):
    return math.atan2(environment["args"]["a"], environment["args"]["b"])

@create_function("FLOAT", {"a": "FLOAT"})
def atanh(environment):
    return math.atanh(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def acos(environment):
    return math.acos(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def asin(environment):
    return math.asin(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def acosh(environment):
    return math.acosh(environment["args"]["a"])

@create_function("FLOAT", {"a": "FLOAT"})
def asinh(environment):
    return math.asinh(environment["args"]["a"])

@create_function("INT", {"a": "FLOAT"})
def ceil(environment):
    return math.ceil(environment["args"]["a"])

@create_function("INT", {"a": "FLOAT"})
def floor(environment):
    return math.floor(environment["args"]["a"])

@create_function("INT", {"a": "FLOAT"})
def ftoi(environment):
    return int(environment["args"]["a"])

@create_function("FLOAT", {"a": "INT"})
def itof(environment):
    return float(environment["args"]["a"])

rsxmath = pack_library()