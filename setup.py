# coding:utf8
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xpath-parser",
    version="0.0.1",
    author="dytttf",
    author_email="1821367759@qq.com",
    description="A xpath expression parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dytttf/xpath-parser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
