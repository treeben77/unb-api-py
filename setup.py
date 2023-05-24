from setuptools import setup

import re

with open("unbapi/__init__.py", "r") as file:
    version = re.search(r"VERSION: str = \"(\d+\.\d+\.\d+)\"", file.read()).group(1)

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='unbapi',
    description='API wrapper for the UnbelievaBoat Discord bot in Python',
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    python_requires='>=3.9.0',
    author="TreeBen77",
    packages=[
        'unbapi'
    ],
    url='https://github.com/TreeBen77/unb-api-py',
    keywords='',
    install_requires=[
        'requests'
    ]
)
