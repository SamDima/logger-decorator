import setuptools
from setuptools import setup

VERSION="2.3.1"

setup(
    name="logger-decorator",
    author="Dmitriy Ignatiev",
    author_email="dmitrignatyev@gmail.com",
    version=VERSION,
    py_modules=["logger_decorator"],
    description="Logger decorator with request id",
    long_description="""
    Logger decorator with log request_id (optionally)
    """,
    install_requires=[
        "loguru"
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6'
)
