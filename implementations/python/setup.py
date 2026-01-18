"""
Setup script for the Cascading Agent Architecture package.
"""

from setuptools import setup, find_packages
import os


# Read README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements


setup(
    name="cascading-agent",
    version="1.0.0",
    description="Reference implementation of the Cascading Agent Architecture for Memory Retrieval",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Jason Faulkner",
    author_email="",
    url="https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval",
    packages=find_packages(exclude=["tests", "benchmarks", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0,<2.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
        ],
        "embeddings": [
            "sentence-transformers>=2.2.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="agent memory retrieval cascading architecture ai ml",
    project_urls={
        "Bug Reports": "https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval/issues",
        "Source": "https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval",
        "Documentation": "https://github.com/theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval/tree/main/docs",
    },
)
