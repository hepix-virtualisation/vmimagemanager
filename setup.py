from vmim.__version__ import version
from sys import version_info


if version_info < (2, 6):
    import sys
    print ("Please use a newer version of python")
    sys.exit(1)

if version_info < (2, 7):
    from distutils.core import setup
    import sys

if version_info > (2, 7):
    try:
        from setuptools import setup, find_packages
    except ImportError:
	    try:
                from distutils.core import setup
	    except ImportError:
                from ez_setup import use_setuptools
                use_setuptools()
                from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand
import sys

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)
            
setup(name='vmimagemanager',
    version=version,
    description="vmimagemanager manages virtual maschines",
    author="O M Synge",
    author_email="owen.Synge@desy.de",
    url="www-it.desy.de",
    scripts = ["vmimagemanager"],
    package_dir={'': '.'},
    packages=['vmim', 'vmim/tests'],
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
        'pytest',
    ],
    setup_requires=[
        'pytest',
    ],
    cmdclass = {'test': PyTest},
    )

