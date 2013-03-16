from setuptools import setup
from peek import VERSION

setup(
    name="PyPeek",
    version=VERSION,
    description="Cross-platform and Cross-backend screenshot library.",
    long_description="Has a lot of backends: pywin32, PIL, gtk, QT, wx, " +
                     "scrot and imagemagick",
    author="Jeppe Klitgaard",
    author_email="jeppe@dapj.dk",
    url="https://github.com/dkkline/PyPeek",
    license="apache 2",
    py_modules=["peek"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities"]
)
