import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

long_description = (HERE / "README.md").read_text()


def get_version() -> str:
    fpath = HERE / "check_patroni" / "__init__.py"
    with fpath.open() as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split('"')[1]
    raise Exception(f"version information not found in {fpath}")


setup(
    name="check_patroni",
    version=get_version(),
#    author="Dalibo",
#    author_email="contact@dalibo.com",
    packages=find_packages("."),
    include_package_data=True,
#    url="https://github.com/dalibo/pg_activity",
    license="PostgreSQL",
    description="Nagios plugin to check on patroni",
    long_description=long_description,
    long_description_content_type="text/markdown",
#    classifiers=[
#        "Development Status :: 5 - Production/Stable",
#        "Environment :: Console",
#        "License :: OSI Approved :: PostgreSQL License",
#        "Programming Language :: Python :: 3",
#        "Topic :: Database",
#    ],
    keywords="patroni nagios cehck",
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "black",
            "check-manifest",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "check_patroni=check_patroni.cli:main",
        ],
    },
    zip_safe=False,
)
