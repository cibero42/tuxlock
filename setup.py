from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme:
    long_description=readme.read()

setup(
    name="tuxlock",
    version="0.1.0",
    description="Tuxlock is a program that helps SysAdmins on securing their Linux servers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="cibero42",
    author_email="cibero42@cibero.net",
    license="AGPLv3",
    packages=["tuxlock"],
    package_dir={"tuxlock":"tuxlock"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPLv3",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts":["tucklock=tuxlock.tuxlock:main"]
    },
    keywords="tuxlock",
    python_requires=">=3.11"
)