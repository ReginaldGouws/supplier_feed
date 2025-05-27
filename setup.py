from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in supplier_feed/__init__.py
from supplier_feed import __version__ as version

setup(
	name="supplier_feed",
	version=version,
	description="Manage and import supplier feeds in XML, CSV, and JSON format",
	author="Your Company",
	author_email="your.email@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)