#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", "r") as reqs_file:
    requirements = reqs_file.readlines()

with open("requirements_dev.txt", "r") as reqs_dev_file:
    test_requirements = reqs_dev_file.readlines()

setup_requirements = ["pytest-runner"]

setup(
    author="Vagif Mammadaliyev",
    author_email="vagifmammadaliyev@outlook.com",
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Tool for easier switching between projects that uses docker containers to set up working environment",
    entry_points={
        "console_scripts": [
            "dockswap=dockswap.cli:app",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="dockswap",
    name="dockswap",
    packages=find_packages(include=["dockswap", "dockswap.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/VagifMammadaliyev/dockswap",
    version="0.3.0",
    zip_safe=False,
)
