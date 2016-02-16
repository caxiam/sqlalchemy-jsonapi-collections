"""Flask-SQLAlchemy-JSONAPI.

A URL parsing library that uses documented JSONAPI 1.0 specification
URL parameters to filter, sort, and include JSONAPI response objects.
"""
from setuptools import find_packages, setup


setup(
    name='Flask-SQLAlchemy-JSONAPI',
    version='0.1',
    url='https://github.com/caxiam/sqlalchemy-jsonapi-collections',
    license='BSD',
    author='Colton Allen',
    author_email='colton.allen@caxiam.com',
    description='A collection response filtering library.',
    long_description=__doc__,
    packages=find_packages(exclude=("test*", )),
    package_dir={'flask-sqlalchemy-jsonapi': 'flask-sqlalchemy-jsonapi'},
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask', 'SQLAlchemy', 'marshmallow', 'marshmallow-jsonapi'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='tests'
)
