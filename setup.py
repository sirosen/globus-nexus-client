import os.path
from typing import Any, Dict

from setuptools import setup

# single source of truth for package version
version_ns = {}  # type: Dict[str, Any]
with open(os.path.join("globus_nexus_client", "version.py")) as f:
    exec(f.read(), version_ns)

setup(
    name="globus-nexus-client",
    version=version_ns["__version__"],
    description="Unofficial Globus Nexus Client (based on SDK clients)",
    long_description=open("README.rst").read(),
    author="Stephen Rosen",
    author_email="support@globus.org",
    url="https://github.com/sirosen/globus-nexus-client",
    packages=["globus_nexus_client"],
    install_requires=["globus-sdk==3.0.0a1"],
    keywords=["globus", "groups", "nexus"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
