from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='quant-crawler',
    version='0.0.1',

    author='agutong',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/',

    license='LICENSE',
    description='quant crawler',
    long_description=open('README.md').read(),

    packages=[
      'quant_crawler'
    ],

    data_files=[
        #('bitmaps', ['bm/b1.gif', 'bm/b2.gif']),
        #('/etc/agutong.cfg', ['cfg/data.cfg']),
        #('/etc/init.d', ['bin/init-script'])
    ],

    scripts=[
        'bin/quant-crawler'
    ],

    install_requires=[
        "requests",
        "grequests",
        "pyquery",
        "PyExecJS",
        "objgraph",
        "chardet",
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
