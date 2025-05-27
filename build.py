#!/bin/python3.11

import os
import argparse

from subprocess import call

from eltextool.textypes.version import Version


def main(
    package,
    dev: bool = True,
    patch: bool = False,
    minor: bool = False,
    major: bool = False,
    install: bool = True,
):
    current_version = Version(package.__version__)
    new_version = Version(package.__version__)
    print("Current version:", current_version)

    if dev:
        next(new_version)

    if patch:
        new_version.patch()

    if minor:
        new_version.minor()

    if major:
        new_version.major()

    print("New version:", new_version)

    with open("version", "w") as file:
        file.write(str(new_version))

    call(["python3.11", "setup.py", "sdist"])

    call(["rm", "-r", f"{package.__name__}.egg-info"])

    with open(f"{package.__name__}/__init__.py", "r+") as file:
        old_init = file.read()
    new_init = old_init.replace(str(current_version), str(new_version))

    with open(f"{package.__name__}/__init__.py", "w") as file:
        file.write(new_init)

    try:
        os.remove(f"{package.__name__}-{current_version}.tar.gz")
    except FileNotFoundError as ex:
        print(ex)

    os.rename(
        f"dist/{package.__name__}-{new_version}.tar.gz",
        f"{package.__name__}-{new_version}.tar.gz",
    )

    if install:
        call(
            [
                "python3.11",
                "-m",
                "pip",
                "install",
                f"{package.__name__}-{new_version}.tar.gz",
            ]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str)
    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument("--dev", action="store_true")
    group.add_argument("--patch", action="store_true")
    group.add_argument("--minor", action="store_true")
    group.add_argument("--major", action="store_true")
    group.add_argument("--noinstall", action="store_false")
    group.add_argument("--rebuild", action="store_true")

    args = parser.parse_args()

    package = __import__(args.name)

    main(package, args.dev, args.patch, args.minor, args.major, args.noinstall)
