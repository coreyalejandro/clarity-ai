from setuptools import setup, find_packages

setup(
    name="clarity-ai",
    version="0.1.0",
    description="Train LLMs with teacher-style rubrics",
    author="ClarityAI",
    packages=find_packages(),
    install_requires=[
        "torch>=1.9.0",
        "transformers>=4.20.0",
        "trl>=0.4.0",
        "streamlit>=1.20.0",
        "pyyaml>=6.0",
        "numpy>=1.21.0",
    ],
    entry_points={
        "console_scripts": [
            "clarity=clarity.cli:main",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)