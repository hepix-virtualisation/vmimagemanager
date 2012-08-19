import os
import logging, logging.config
import sys
import optparse


from __version__ import version 
def usage():
    print "usage"

def start():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    ch.setFormatter(formatter)
    #add ch to logger
    
    logging.basicConfig(level=logging.WARNING)
    vmimlog = logging.getLogger("vmimagemanager")
    #vmimlog.setLevel(logging.DEBUG)
    vmimlog.addHandler(ch)
    
    InstallPrefix="/"

    ConfigFile = ""

    Fillocations = ['/etc/vmimagemanager/vmimagemanager.cfg']

    for fileName in Fillocations:
	    if True == os.path.isfile(fileName):
		    ConfigFile = fileName
		    break
    if len(ConfigFile) == 0:
	    ConfigFile = Fillocations[0]
    logger = logging.getLogger("vmimagemanager")
    
    #create formatter
    debugFileName = None
    #logging.config.fileConfig("logging.conf")
    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:s:r:e:i:c:D:C:udlLhvkzypfm", ["box=", "store=","restore=","extract=","insert=","config=","cpu","up","down","list-boxes","list-images","help","version","kill","tgz",c,"rsync","print-config","free","locked"])
    except :
        usage()
        logger.error('Command line option error')
        sys.exit(1)
    





def main():
    log = logging.getLogger("main")
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-b', '--box', action ='append',help="Select 'boxes' to operate.")
    p.add_option('-s', '--store', action ='append', help='Database Initiation string')
    p.add_option('-r', '--restore', action ='append',help='Add endorser in your subscribe to imagelist action.')
    p.add_option('-e', '--extract', action ='append',help='Certificate directory.', metavar='INPUTDIR')
    p.add_option('-i', '--insert', action ='append',help='Select subscription', metavar='UUID')
    p.add_option('-c', '--config', action ='append',help='Select subscription', metavar='URL')
    p.add_option('--cpu', action ='store',help='Sets the output format')
    p.add_option('-u', '--up', action ='store_true',help='Delete subscription')
    p.add_option('-d', '--down', action ='store_true',help='Information on subscription')
    p.add_option('-l', '--list-boxes', action ='store_true',help='Export File.', metavar='OUTPUTFILE')
    p.add_option('-L', '--list-images', action ='store_true',help='Logfile configuration file.', metavar='LOGFILE')
    #p.add_option('-v', '--version', action ='store_true',help='Event application to launch.', metavar='EVENT')    
    p.add_option('-k', '--kill', action ='store_true',help='Export File.', metavar='OUTPUTFILE')
    p.add_option('-z', '--tgz', action ='store_true',help='Logfile configuration file.', metavar='LOGFILE')
    p.add_option('-y', '--rsync', action ='store_true',help='Event application to launch.', metavar='EVENT')
    p.add_option('-w', '--cpio-bzip', action ='store_true',help='Event application to launch.', metavar='EVENT')
    
    p.add_option('-o', '--print-config', action ='append',help='Export File.', metavar='OUTPUTFILE')
    p.add_option('--logfile', action ='store',help='Logfile configuration file.', metavar='LOGFILE')
    
    
    
    options, arguments = p.parse_args()
    # OptionValues
    logFile = None
    actions = set()
    ConfigurationFilePath = '/etc/vmimagemanager/vmimagemanager.cfg'
    
    DefaultConfigurationPath = None
    if 'VMIM_CFG' in os.environ:
        ConfigurationFilePath = os.environ['VMIM_CFG']
    if 'VMIM_LOG_CONF' in os.environ:
        logFile = os.environ['VMILS_LOG_CONF']
    
    # Set up log file
    if options.logfile:
        logFile = options.logfile
    if logFile != None:
        if os.path.isfile(str(options.logfile)):
            logging.config.fileConfig(options.logfile)
        else:
            logging.basicConfig(level=logging.INFO)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.logfile))
            sys.exit(1)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")
    # Now logging is set up process other options
    if options.box:
        box = options.box
    if options.store:
        store = options.store
    if options.restore:
        restore = options.restore
    if options.insert:
        insert = options.insert
    if options.extract:
        extract = options.extract
    if options.config:
        config = options.config
    if options.cpu:
        cpu = options.cpu
    if options.up:
        store = options.store
    if options.down:
        store = options.store
    if options.list_boxes:
        store = options.store
    if options.list_images:
        store = options.store
    if options.kill:
        store = options.store
    if options.tgz:
        store = options.store
    if options.rsync:
        store = options.store
    if options.cpio_bzip:
        store = options.store
    if options.print_config:
        store = options.store

    # 1 So we have some command line validation
    if len(actions) == 0:
        log.error("No actions selected")
        sys.exit(1)
    if len(actions) > 1:
        log.error("More than one action selected.")
        sys.exit(1)
    if format_needed and len(output_format_selected) == 0:
        log.error("No output format selected")
        sys.exit(1)

    # 1.1 Initate DB
    database = db_controler(databaseConnectionString)
    # 1.2 Set up callbacks
    if eventExecutionString != None:
        EventInstance = EventObj(eventExecutionString)
        database.callbackEventImageNew = EventInstance.eventImageNew
    
    # 2 Initate CA's to manage files
    if anchor_needed:
        if certDir == None:
            certDir = "/etc/grid-security/certificates/"
            log.info("Defaulting Certificate directory to '%s'" % (certDir))
        database.setup_trust_anchor(certDir)

    # Handle conflicting actions
    actions_req_sel = actionsrequiring_selections.intersection(actions)

    actions_req_sel_len = len(actions_req_sel)
    if actions_req_sel_len == 1:
        if len(subscriptions_selected) == 0:
            log.error('No selections made.')
            sys.exit(1)
    if actions_req_sel_len > 1:
        log.error('Conflicting functions.')
        sys.exit(1)
    # Handle conflicting identifiers

    selectors_types = inputformats.intersection(input_format_selected)
    selectors_types_len = len(selectors_types)
    if selectors_types_len > 1:
        log.error('Conflicting selectors.')
        sys.exit(1)







if __name__ == "__main__":
    main()
    
