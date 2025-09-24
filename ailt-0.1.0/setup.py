from setuptools import setup, find_packages

setup(
    name="ailt",  # Python package name
    version="0.1.0",
    packages=find_packages(include=["ailt", "ailt.*"]),
    include_package_data=True,
    install_requires=[
        "requests",
        "rich",
        "distro",
        "prompt_toolkit",
    ],

    entry_points={
        "console_scripts": [
            "ailt=ailt.main:run",  # creates the 'ailt' CLI command
        ],
    },
    python_requires=">=3.8",
    author="Luka Beslic",
    author_email="devluka.public@gmail.com",
    description="AILT - AI Linux Terminal",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://yourwebsite.com/ailt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
