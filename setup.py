"""Package metadata for the webstore API."""

from setuptools import find_packages, setup


setup(
    name="webstore",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask>=3.0",
        "Flask-RESTful>=0.3.10",
        "Flask-SQLAlchemy>=3.1",
        "jsonschema>=4.0",
        "requests>=2.28",
    ],
)
