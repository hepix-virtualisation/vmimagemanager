from vmim.__version__ import version
from sys import version_info

if version_info < (2, 6):
	from distutils.core import setup
else:
	try:
        	from setuptools import setup, find_packages
	except ImportError:
        	from ez_setup import use_setuptools
        	use_setuptools()
        	from setuptools import setup, find_packages


            
setup(name='vmimagemanager',
    version=version,
    description="vmimagemanager manages virtual maschines",
    author="O M Synge",
    author_email="owen.Synge@desy.de",
    url="www-it.desy.de",
    scripts = ["vmimagemanager"],
    package_dir={'': '.'},
    packages=['vmim'],
    data_files=[('/usr/bin/', ['vmimagemanager']),
('/etc/vmimagemanager',['libvirt.xsl','vmimagemanager.cfg.template']),
('/usr/share/doc/vmimagemanager',['README']),
('/usr/share/doc/vmimagemanager/examples',['docs/examples/vmimagemanager-example-au.cfg',
'docs/examples/vmimagemanager-example-au.cfg',
'docs/examples/vmimagemanager-example-d430.cfg',
'docs/examples/vmimagemanager-example-esys.cfg',
'docs/examples/vmimagemanager-example-irl.cfg',
'docs/examples/vmimagemanager-example-whitehouse.cfg',
'docs/examples/vmimagemanager-xen-example.template',
'docs/examples/xen.template',
'docs/examples/xen.template.example.full.virtualisation',
'docs/examples/logging.conf',
'docs/examples/libvirt-redhat-el-6.xsl',
'docs/examples/libvirt-redhat-el-5.xsl'])],
    tests_require=[
        'coverage >= 3.0',
        'nose >= 1.1.0',
        'mock',
    ],
    setup_requires=[
        'nose',
    ],
    test_suite = 'nose.collector',
    )

