from setuptools import setup, find_packages


setup(
    name="tds",
    version="0.0.1",
    description="Table Data Sync",
    author="Linewalks",
    author_email="insu@linewalks.com",
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
            "tds = main.run:main"
        ]
    },
    package_data={"main": ["sql/*.sql","sql/**/*.sql"]},
    include_package_data=True
)
