from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='pyqtetreemodel',
      version='0.2',
      description='qt tree model for lxml.etree representations of xml',
      long_description=readme(),
      url='None',
      author='Jennifer Holt',
      author_email='jholt1978@gmail.com',
      license='MIT',
      packages=['pyqtetreemodel'],
      install_requires=[
          'pyqtgraph',
          'lxml',
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'])
