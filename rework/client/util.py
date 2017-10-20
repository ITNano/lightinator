import logging
import pkgutil

"""
  Loads the available modules from the given path. Code inspired by the Brain
  class in the jasper project by Shubhro Saha, Charles Marsh and Jan Holthuis.
  https://github.com/jasperproject/jasper-client/blob/master/client/brain.py
"""
def load_folder_modules(path, accept_func=None):
    logger = logging.getLogger(__name__)
    logger.debug("Searching for modules in folder: "+path);
    modules = {}
    for finder, name, ispkg, in pkgutil.walk_packages([path]):
        try:
            loader = finder.find_module(name)
            mod = loader.load_module(name)
            
            logger.info("Loaded module '%s'", name)
            if accept_func is None or accept_func(name, mod):
                modules[name] = mod
        except:
            logger.warning("Skipped module '%s' due to mysterious error", name, exc_info=True)
                
    return modules
    
    
def run_daemon(target, args=None):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()