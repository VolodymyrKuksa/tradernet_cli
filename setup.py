import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tradernet_cli",
    version="1.0.3",
    author="Volodymyr Kuksa",
    author_email="volodymyrkuksa@gmail.com",
    description="A small TraderNet API (https://tradernet.com/) client for automation purposes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VolodymyrKuksa/tradernet_cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests'],
    python_requires='>=3.7',
)
