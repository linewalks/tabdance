from setuptools import setup, find_packages


setup(
    name="tabdanc",
    version="0.0.1",
    description="Table Data Sync",
    author="Linewalks",
    author_email="insu@linewalks.com",
    url="https://github.com/linewalks/tabdanc",
    python_requires=">= 3.8",
    packages=find_packages(),
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
            "tabdanc = tds.run:main"
        ]
    },
    package_data={"tabdanc": ["tds.default.cfg", "sql/*.sql", "sql/**/*.sql"]},
    include_package_data=True
)
