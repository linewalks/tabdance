import os
from setuptools import setup, find_packages


def read_requirements():
  with open(os.path.join(os.getcwd(), "requirements.txt"), "r") as file:
    packages = []
    for line in file.readlines():
      packages.append(line.strip())  
  print(packages)
  return packages

setup(
    name="tds",
    version="0.0.1",
    description="Table Data Sync",
    author="Linewalks",
    author_email="insu@linewalks.com",
    python_requires=">= 3.8",
    packages=find_packages(),
    install_requires=read_requirements(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "tds = main.updownload:main"
        ]
    }
)
