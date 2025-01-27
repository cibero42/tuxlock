setup(
    name="tuxlock",
    version="0.1.0",
    description="Simplify Linux hardening",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cibero42/tuxlock",
    author="Cibero42",
    author_email="cibero42@cibero.net",
    license="AGPLv3",
    classifiers=[
        "License :: OSI Approved :: AGPLv3 License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["tuxlock"],
    include_package_data=True,
    install_requires=[
        "inquirer"
    ],
    entry_points={"console_scripts": ["tuxlock=tuxlock.__main__:main"]},
)
