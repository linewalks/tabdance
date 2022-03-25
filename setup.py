from setuptools import setup, find_packages


setup(
    name="tabdance",
    version="1.0.2",
    description="Table Data Syncer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Linewalks",
    author_email="insu@linewalks.com",
    url="https://github.com/linewalks/tabdance",
    python_requires=">= 3.8",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "configparser",
        "paramiko",
        "pandas",
        "psycopg2-binary",
        "SQLAlchemy"
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "tabdance = tabdance.run:main"
        ]
    },
    package_data={"tabdance": ["tabdance.default.cfg", "sql/*.sql", "sql/**/*.sql"]},
    include_package_data=True
)
