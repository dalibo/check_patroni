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
    author="Dalibo",
    author_email="contact@dalibo.com",
    packages=find_packages(include=["check_patroni*"]),
    include_package_data=True,
    url="https://github.com/dalibo/check_patroni",
    license="PostgreSQL",
    description="Nagios plugin to check on patroni",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",  # "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: PostgreSQL License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Monitoring",
    ],
    keywords="patroni nagios check",
    python_requires=">=3.6",
    install_requires=[
        "attrs >= 17, !=21.1",
        "urllib3 >= 1.26.6",
        "nagiosplugin >= 1.3.2",
        "click >= 8.0.1",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-mock",
        ],
    },
    entry_points={
        "console_scripts": [
            "check_patroni=check_patroni.cli:main",
        ],
    },
    zip_safe=False,
)
