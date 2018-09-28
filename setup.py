from setuptools import setup, find_packages

reqs = [
    "asyncssh",
]

setup(
    name='sshleme',
    packages=find_packages(),
    install_requires=reqs,
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'sshleme=sshleme.run:main'
        ]
    }
)
