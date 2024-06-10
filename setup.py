import os
from setuptools import setup

README_PATH = 'README.rst'
LONG_DESC = ''
if os.path.exists(README_PATH):
    with open(README_PATH) as readme:
        LONG_DESC = readme.read()

INSTALL_REQUIRES = ['lxml','pysimplesoap','requests']
PACKAGE_NAME = 'pyCFE'
PACKAGE_DIR = 'src'

setup(
    name=PACKAGE_NAME,
    version='0.0.22',
    author='Alex Cuellar',
    author_email='acuellar@grupoyacck.com',
    maintainer='Alex Cuellar',
    maintainer_email='acuellar@grupoyacck.com',
    description=(
        "Facturacion Electronica Uruguaya"
    ),
    long_description=LONG_DESC,
    long_description_content_type='text/markdown',
    license='GPLv3',
    keywords='pyCFE',
    url='',
    packages=[PACKAGE_NAME,"%s.common"%PACKAGE_NAME,
              "%s.efactura"%PACKAGE_NAME,
              "%s.biller"%PACKAGE_NAME, "%s.facturaexpress"%PACKAGE_NAME],
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': ['{0} = {0}.{0}:main'.format(PACKAGE_NAME)]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
