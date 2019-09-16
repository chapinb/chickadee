import setuptools

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='chickadee',
    version=20190915,
    description='Yet another GeoIP resolution tool.',
    author='Chapin Bryce',
    author_email='python@chapinb.com',
    url='https://github.com/chapinb/chickadee',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'chickadee = libchickadee.chickadee:entry'
        ]
    },
    install_requires=[
        "requests >= 2.22.0",
        "openpyxl >= 2.6.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]

)