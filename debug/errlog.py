import traceback
import sys

def dumpThreads():
    print "\n*** STACKTRACE - START ***\n"
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename,lineno, name))
            if line:
                code.append(" %s" % (line.strip()))

    for line in code:
        print line
    print "\n*** STACKTRACE - END ***\n"
