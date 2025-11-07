"""
Setup файл для DateReg API Library
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README для длинного описания
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="datereg",
    version="1.0.0",
    author="DateReg Library",
    description="Python библиотека для работы с DateRegBot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/C0dwiz/DateReg-lib",
    packages=find_packages(),
    package_data={
        "datereg": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
    ],
    keywords="telegram datereg api date registration",
    project_urls={
        "Documentation": "https://docs.goy.guru/api",
        "Source": "https://github.com/C0dwiz/DateReg-lib",
    },
)

