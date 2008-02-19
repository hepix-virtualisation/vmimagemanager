from distutils.core import setup
ProjectName='vmimagemanager'
versionString='0.0.4.1'
docRoot='/usr/share/doc/' + ProjectName + '-' + versionString
setup(name=ProjectName,
        version=versionString,
        description="Virualisation manager, xen template generator and image mover.",
        author="owen synge",
        author_email="owen.synge@desy.de",
        url="http://www.python.org/sigs/distutils-sig/",
        package_dir={'': '.'},     
        data_files=[('/etc/' + ProjectName , ['vmimagemanager.cfg','config/xen.template']),
        (docRoot + '/example-cfg/',[ 'config/vmimagemanager-example-d430.cfg',
        'config/vmimagemanager-example-au.cfg',   'config/vmimagemanager-example-irl.cfg',
        'config/vmimagemanager-example-esys.cfg','config/vmimagemanager-example-whitehouse.cfg']),
        (docRoot, ['README']),
        (docRoot + '/example-template/', ['config/vmimagemanager-xen-example.template']),
        ],
    scripts=['vmimagemanager.py']
)
