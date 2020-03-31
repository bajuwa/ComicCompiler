import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='comic-compiler',
    version='1.0.dev1',
    scripts=['comic-compiler'],
    author="bajuwa",
    author_email="justcallmebaj@gmail.com",
    description="A script that stitches images together and breaks them in to pages based on available whitespace",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bajuwa/ComicCompiler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)Close",
        "Operating System :: OS Independent",
    ],
)
