from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='p2.datashackle.core',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='projekt und partner',
      author_email='mail@projekt-und-partner.de',
      url='http://datashackle.net',
      license='Proprietary',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['p2', 'p2.datashackle'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'SQLAlchemy',
          'sqlalchemy-migrate',
          'MySQL-python',
          'grok',
          'venusian',
          'lxml'
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
