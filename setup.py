from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="PlantvsAi-zombitx64",
    version="2.0.0",
    author="PlantvsAi-zombitx64 Contributors",
    author_email="your-email@example.com",
    description="เกมกระดานหลายรูปแบบพร้อม AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JonusNattapong/PlantvsAi-zombitx64",
    project_urls={
        "Bug Tracker": "https://github.com/JonusNattapong/PlantvsAi-zombitx64/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "PlantvsAi-zombitx64=PlantvsAi_zombitx64.app:main",
        ],
    },
    include_package_data=True,
) 