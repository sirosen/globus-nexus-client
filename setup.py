from setuptools import setup

setup(
    name="globus-nexus-client",
    version="0.4.0a1",
    description="Unofficial Globus Nexus Client (based on SDK clients)",
    long_description=open("README.rst").read(),
    author="Stephen Rosen",
    author_email="support@globus.org",
    url="https://github.com/sirosen/globus-nexus-client",
    py_modules=["globus_nexus_client"],
    install_requires=["globus-sdk==3.0.0a2"],
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
