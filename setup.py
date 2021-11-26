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
        "configparser==5.0.2",
        "paramiko==2.8.0",
        "pandas==1.3.4",
        "SQLAlchemy==1.3.23"
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "tds = main.updownload:main"
        ]
    }
)
