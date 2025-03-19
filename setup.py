from setuptools import setup, find_packages

setup(
    name="john-migrator",  # Change this to a unique name on PyPI
    version="1.0.0",
    author="John Doe",
    author_email="krishnachauhan20993@gmail.com",
    description="A lightweight database migration tool for Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Krishna-chauhan/john-migrator.git",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "psycopg2-binary"
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "db-migrate=src.migrate:main",  # CLI command
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
