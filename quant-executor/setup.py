from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='quant-executor',
    version='0.0.1',

    author='agutong',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/',

    license='LICENSE',
    description='quant executor',
    long_description=open('README.md').read(),

    packages=[
      'quant_executor',
      'quant_executor.executors',
      'quant_executor.plugins',
    ],

    package_data = {
        #'my_package_name': ['config/*.yml'],
    },

    data_files=[
        #('/etc/init.d', ['bin/init-script'])
    ],

    scripts=[
        'bin/quant-executor'
    ],

    install_requires=[
        #"Django >= 1.1.1",
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
