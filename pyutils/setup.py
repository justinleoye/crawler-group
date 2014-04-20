from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='pyutils',
    version='0.0.1',

    author='agutong',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/',

    license='LICENSE',
    description='my package description',
    long_description=open('README.md').read(),

    packages=[
      'pyutils',
      'pyutils.serializers',
    ],

    scripts=[
        #'bin/my_script.py'
    ],

    install_requires=[
        'colorama',
        'colorlog',
        'Jinja2',
        'chardet',
        'PyYAML',
        'pyaml',
        'python-dateutil',
        'parsedatetime',
        'configure',

        #for debug
        'pudb',
    ],
    dependency_links=[
        #zip/tar urls
    ]
)
