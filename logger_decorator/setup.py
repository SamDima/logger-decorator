import setuptools
from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION="3.0.0"

setup(
    name="logger-decorator",
    author="Dmitriy Ignatiev",
    author_email="dmitrignatyev@gmail.com",
    version=VERSION,
    py_modules=["logger_decorator"],
    long_description = long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "loguru"
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6'
)
