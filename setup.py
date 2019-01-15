from setuptools import setup

setup(name='KBE',
      version='1.0',
      description='Utilizing ParaPy to Frontload Preliminary UAV Design',
      url='https://github.com/skilkis/KBE',
      author='San Kilkis, Nelson Johnson',
      author_email='Kilkis@student.tudelft.nl, n.a.johnson@student.tudelft.nl',
      license='MIT',
      packages=['KBE'],
      install_requires=[
          'numpy',
          'parapy',
          'xlrd',
          'xlwt',
          'math',
          'json',
          'matplotlib',
          'scipy',
      ],
      zip_safe=False)
