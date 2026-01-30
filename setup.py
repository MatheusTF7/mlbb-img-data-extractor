"""Setup script for mlbb-img-data-extractor package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mlbb-img-data-extractor",
    version="0.1.0",
    author="MatheusTF7",
    description="Extract structured data from Mobile Legends end-game screenshots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MatheusTF7/mlbb-img-data-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "pytesseract>=0.3.10",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "openpyxl>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mlbb-extract=main:main",
        ],
    },
    keywords="mlbb mobile-legends ocr image-processing data-extraction screenshot",
)
