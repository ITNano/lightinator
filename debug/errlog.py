import traceback
import sys
import logging

def dumpThreads():
    logging.debug("\n*** STACKTRACE - START ***\n")
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,lineno, name))
            if line:
                code.append(" %s" % (line.strip()))

    for line in code:
        logging.debug(line)
    logging.debug("\n*** STACKTRACE - END ***\n")
