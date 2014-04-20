from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='quant-etcd',
    version='0.0.1',

    author='agutong',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/',

    license='LICENSE',
    description='quant etcd',
    long_description=open('README.md').read(),

    packages=[
      'quant_etcd',
    ],

    package_data = {
        #'my_package_name': ['config/*.yml'],
    },

    data_files=[
        #('/etc/init.d', ['bin/init-script'])
    ],

    scripts=[
        'bin/quant-etcd'
    ],

    install_requires=[
        "python-etcd",
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
