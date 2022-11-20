import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyhatchbabyrest",
    version="2.1.0",
    author="Kevin O'Connor",
    author_email="kjoconnor@gmail.com",
    description="Python library to control Hatch Baby Rest devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kjoconnor/pyhatchbabyrest",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Topic :: Home Automation",
    ],
    python_requires=">=3.5",
    install_requires=[
        "bleak",
        "pygatt",
    ],
)
