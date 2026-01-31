"""Setup script for mlbb-img-data-extractor package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mlbb-img-data-extractor",
    version="1.0.0",
    author="MatheusTF7",
    description="Extrai dados de jogadores de screenshots do Mobile Legends Bang Bang",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MatheusTF7/mlbb-img-data-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=[
        "opencv-python>=4.8.0",
        "pytesseract>=0.3.10",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "mlbb-extract=main:main",
        ],
    },
    keywords="mlbb mobile-legends ocr image-processing data-extraction screenshot",
)
