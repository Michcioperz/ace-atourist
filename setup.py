from setuptools import setup, find_packages

setup(
    name="ace-atourist",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["ninja_syntax>=1.7.2,<1.8"],
    author="Michał Sidor",
    author_email="public+pypi@meekchopp.es",
    url="https://git.sr.ht/~michcioperz/ace-atourist",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.7",
    entry_points=dict(console_scripts=["ace-atourist=ace_atourist.main:main"]),
)
