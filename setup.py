from setuptools import setup, find_packages

setup(
    name='liberty_parser',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'colorlog',
    ],
    entry_points={
        'console_scripts': [
            'liberty_parser=main:main',  # TODO: Fix this entry point
        ],
    },
    author='dongruihu',
    author_email='dongruihu@bytedance.com',
    description='A Python software develop kit for working with Synopsys Liberty standard',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hudongrui/liberty_sdk',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)