from setuptools import setup, find_packages


setup(
    name="tabdanc",
    version="0.0.2",
    description="Table Data Sync",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
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
            "tabdanc = tabdanc.run:main"
        ]
    },
    package_data={"tabdanc": ["tabdanc.default.cfg", "sql/*.sql", "sql/**/*.sql"]},
    include_package_data=True
)
