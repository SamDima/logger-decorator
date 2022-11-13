from setuptools import setup

VERSION="0.0.1"

setup(
    name="universal-logger",
    author="Dmitriy Ignatiev",
    author_email="dmitriy.ignatiev83@gmail.com",
    version=VERSION,
    py_modules=["universal_logger"],
    description="Universal logger decorator",
    long_description="""
    Universal logger decorator with log request_id (optionally)
    """,
    install_requires=[
        "loguru"
    ]
)
