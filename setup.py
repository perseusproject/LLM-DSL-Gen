from setuptools import setup, find_packages
import sys

install_requires = [
    'unstructured>=0.16.17',
    'langchain-chroma>=0.2.1',
    'langchain-community>=0.3.16',
    'langchain-core>=0.3.33',
    'langchain-huggingface>=0.1.2',
    'langchain-ollama>=0.2.3',
    'langchain-openai>=0.3.3',
    'langchain-text-splitters>=0.3.5',
    'langdetect>=1.0.9',
    'langgraph>=0.2.68',
    'langgraph-checkpoint>=2.0.10',
    'langgraph-sdk>=0.1.51',
    'langchain>=0.3.16',
    'python-magic>=0.4.27',
    'openai>=1.60.2',
    'tomli>=2.2.1',
    'pydantic>=2.10.6',
    'faiss-cpu>=1.10.0',
    'sentence-transformers>=3.4.1',
]

if sys.platform == 'win32':
    install_requires.append('python-magic-bin==0.4.14')
    install_requires.append('pre-commit')

setup(
    name='llm-dsl-gen',
    version='0.1.0',
    packages=find_packages(include=['dsl_gen*'], exclude=['tests*']),
    install_requires=install_requires,
    extras_require={
        'dev': [
            'tqdm',
            'ipython',
        ],
    },
    author='Yiming CHEN, Yuran ZOU, Atrhur BUIS, Thibaud MONTAGNE, Eric ORDOQUY',
    author_email='yiming.chen@polytechnique.edu',
    description='Lokad\'s domain specific language generator based on LLM',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/saturntsen/llm-dsl-gen',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Proprietary',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
