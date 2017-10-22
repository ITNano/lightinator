import application
import mq
import logging
import logging.config

if __name__ == "__main__":
    print("=================================")
    print("==== STARTING LIGHT SERVER ======")
    print("=================================")
    logging.basicConfig(level=logging.DEBUG)
    #logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(__name__)
    
    application.init()
    while(True):
        cmd = input()
        if cmd == "end":
            break
        else:
            logger.info("Unknown command. Duh.")