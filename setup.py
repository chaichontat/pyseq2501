from setuptools import setup

setup(
    name="PySeq2501",
    version="0.0.1",
    description="A example Python package",
    url="https://github.com/chaichontat",
    author="Chaichontat Sriworart",
    author_email="shudson@anl.gov",
    license="GPL",
    packages=["src"],
    install_requires=[
        "numpy",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.10",
    ],
)
