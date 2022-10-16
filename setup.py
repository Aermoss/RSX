from setuptools import setup, find_packages

import os, sys

with open("README.md", "r", encoding = "UTF-8") as file:
    long_desc = file.read()

with open("MANIFEST.in", "w") as file:
    manifest = "include rsxpy/*\ninclude rsxpy/raid/*\n"

    for i in os.listdir("rsxpy/include"):
        manifest += f"include rsxpy/include/{i}/*\n"

    file.write(manifest)

setup(
    name = "rsxpy",
    version = "0.1.0",
    entry_points = {
        "console_scripts": [
            "rsxpy = rsxpy.core:main",
            "raidpy = rsxpy.raidpy.core:main"
        ]
    },
    description = "An interpreted statically typed multi paradigm general purpose programming language designed for cross platform applications.",
    long_description = long_desc,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Aermoss/RSX",
    author = "Yusuf Rencber",
    author_email = "aermoss.0@gmail.com",
    license = "MIT",
    keywords = [],
    packages = find_packages(),
    include_package_data = True,
    install_requires = ["raylib", "pyinstaller", "pysdl2", "pysdl2-dll"]
)