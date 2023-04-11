from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in dongwoo/__init__.py
from dongwoo import __version__ as version

setup(
	name="dongwoo",
	version=version,
	description="hrms customization for Dongwoo",
	author="TEAMPRO",
	author_email="veeramayandi.p@groupteampro.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
