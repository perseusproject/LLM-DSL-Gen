from setuptools import setup, find_packages

setup(
    name='llm-dsl-gen',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'unstructured',
        'unstructured[md]',
        'langchain',
        'langchain-core',
        'langchain-community',
        'langchain-ollama',
        'python-magic',
        'python-magic-bin',
        'openai',
    ],
    author='Yiming CHEN, Yuran ZOU, Atrhur BUIS, Thibaud MONTAGNE, Eric ORDOQUY',
    author_email='yiming.chen@polytechnique.edu'
    description='Lokad's domain specific language generator based on LLM',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/saturntsen/llm-dsl-gen',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Proprietary',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)