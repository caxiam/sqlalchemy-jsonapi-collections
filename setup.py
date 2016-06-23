"""jsonapi-query.

A JSONAPI compliant query library.
"""
from setuptools import find_packages, setup


setup(
    name='jsonapi-query',
    version='0.2',
    url='https://github.com/caxiam/sqlalchemy-jsonapi-collections',
    license='Apache Version 2.0',
    author='Colton Allen',
    author_email='colton.allen@caxiam.com',
    description='A JSONAPI compliant query library.',
    long_description=__doc__,
    packages=find_packages(exclude=("test*", )),
    package_dir={'src': 'src'},
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='tests'
)
