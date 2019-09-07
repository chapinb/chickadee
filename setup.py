import setuptools

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='chickadee',
    version=20190907,
    description='Yet another GeoIP resolution tool.',
    author='Chapin Bryce',
    author_email='python@chapinb.com',
    url='https://github.com/chapinb/chickadee',
    license='GPLv3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'chickadee = libchickadee.chickadee:__entry__'
        ]
    },
    install_requires=[
        "requests >= 2.22.0",
        "unicodecsv >= 0.14.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]

)