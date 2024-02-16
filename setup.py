from setuptools import setup, find_packages

setup(
    name='codesembench', 
    version='0.0.1',
    python_requires='>3.10',
    description='Semantic benchmark for code LLMs.',
    author='Google LLC',
    author_email='your_email@example.com',
    packages=find_packages(),  # Automatically finds packages
    install_requires=[
	"epath",
	"pytest"
    ]
)
