from setuptools import setup, find_packages

setup(
    name='APP_NAME',
    version='VERSION_INFO',
    packages=find_packages(),
    install_requires=[
        'colorlog',
    ],
    # entry_points={
    #     'console_scripts': [
    #         'liberty_sdk=main:main',  # TODO: For command-line tool entry: klib dump -i cell.lib -o cell.json
    #     ],
    # },
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
    license="GNU License",
)