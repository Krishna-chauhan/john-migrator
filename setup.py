from setuptools import setup, find_packages

setup(
    name="john-migrator",
    version="1.2.0",
    author="John Doe",
    author_email="krishnachauhan20993@gmail.com",
    description="A lightweight database migration tool for Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Krishna-chauhan/john-migrator.git",
    packages=find_packages(include=["src", "src.*"]),
    package_dir={"": "."},  # Point to the root folder
    package_data={
        "src": ["migrations/*.py"],  # Include all migration files
    },
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "john-migrator=src.cli:main",  # Use new CLI
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="database migration sqlalchemy postgresql mysql",
    project_urls={
        "Bug Reports": "https://github.com/Krishna-chauhan/john-migrator/issues",
        "Source": "https://github.com/Krishna-chauhan/john-migrator",
    },
)
