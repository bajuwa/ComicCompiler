import setuptools

from comiccompiler import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='comicom',
    version=version.full,
    scripts=['comicom.py', 'comgui-launcher.py', 'cc-suite.py'],
    author="bajuwa",
    author_email="justcallmebaj@gmail.com",
    description="A script that stitches images together and breaks them in to pages based on available whitespace",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bajuwa/ComicCompiler",
    packages=setuptools.find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    package_data={'comiccompiler': ['resources/pow_icon.ico']},
    include_package_data=True,
    install_requires=[
        'requests',
        'natsort',
        'pillow'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        # "LICENSE :: OSI APPROVED :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)
