from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='ytcj-quotation-crawler',
    version='0.0.1',

    author='agutong',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/',

    license='LICENSE',
    description='ytcj quotation crawler',
    long_description=open('README.md').read(),

    packages=[
      'ytcj_quotation_crawler',
    ],

    package_data = {
        #'my_package_name': ['config/*.yml'],
    },

    data_files=[
        #('/etc/init.d', ['bin/init-script'])
    ],

    scripts=[
        #'bin/my_script.py'
    ],

    install_requires=[
        #"Django >= 1.1.1",
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
