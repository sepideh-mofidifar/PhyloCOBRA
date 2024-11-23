from setuptools import setup, find_packages

setup(
    name="PhyloMICOM",  # The name of your package
    version="0.1.0",  # Version of your package
    author="Sepideh Mofidifar",  # Your name or organization
    author_email="s.mofidifar@gmail.com",  # Your email
    description="A package for microbial community analysis",  # Short description of the package
    long_description=open('README.md').read(),  # Long description read from the README file
    url="https://github.com/sepideh-mofidifar/PhyloMICOM",  # URL of the GitHub repository
    packages=find_packages(),  # Automatically find all the sub-packages (like micom, data, analysis)
    install_requires=[  # External dependencies (if any)
        "micom",  # Include micom if it's a dependency
        "cobra",  # Example, adjust based on your package's needs
    ],
    classifiers=[  # Optional: classifiers help users find your project
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Minimum Python version
)
