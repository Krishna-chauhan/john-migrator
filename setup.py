from setuptools import setup, find_packages

setup(
    name="john-migrator",
    version="1.0.0",
    author="John Doe",
    author_email="krishnachauhan20993@gmail.com",
    description="A lightweight database migration tool for Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Krishna-chauhan/john-migrator.git",
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"": "."},  # Point to the root folder
    package_data={
        "src": ["config.py"],  # Include config.py explicitly
    },
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "john-migrator=src.migrate:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
