from distutils.core import setup
setup(name='vmimagemanager',
      version='0.0.4',
      description="Virualisation image mover",
      author="owen synge",
      author_email="owen.synge@desy.de",
      url="http://www.python.org/sigs/distutils-sig/",
      package_dir={'': '.'},     
      data_files=[('/etc/vmimagemanager/',[ 'config/vmimagemanager-example-d430.cfg',
	   'config/vmimagemanager-example-au.cfg',   'config/vmimagemanager-example-irl.cfg',
	    'config/vmimagemanager-example-esys.cfg']),
	   ('/usr/share/doc/vmimagemanager/', ['README']),
       ('/var/lib/vmimagemanager/etc/', ['config/vmimagemanager-xen-example.template'])],
      scripts=['vmimagemanager.py']
      )
