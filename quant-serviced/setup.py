from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='quant-serviced',
    version='0.0.1',

    author='agutong',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/',

    license='LICENSE',
    description='quant-serviced',
    long_description=open('README.md').read(),

    packages=[
      'quant_serviced',
    ],

    package_data = {
        #'my_package_name': ['config/*.yml'],
    },

    data_files=[
        #('/etc/init.d', ['bin/init-script'])
    ],

    scripts=[
        'bin/quant-serviced'
    ],

    install_requires=[
        #"Django >= 1.1.1",
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
