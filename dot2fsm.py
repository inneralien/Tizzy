#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from optparse import OptionParser
import sys
import FSMGen
import logging

__author__        = "Tim Weaver"
__copyright__     = "Very White Atom Designs, 2010"
__creation_date__ = "Thu Sep  2 09:40:29 PDT 2010"
__version__       = '0.1.0'


if __name__ == '__main__':
    LEVELS = {  'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL,
            }

    parser = OptionParser(usage="%prog <options>", version=__version__)
    parser.add_option("-d", "--debug",
                        dest="debug",
                        default='error',
                        help="Run in special debug mode. Valid options are debug, info, warning, error, critical")
    parser.add_option("-c", "--checks",
                        default=False,
                        action='store_true',
                        dest="checks",
                        help="Run some simple error checking")
    parser.add_option("-l", "--long_messages",
                        default=False,
                        action='store_true',
                        dest="long_messages",
                        help="Print out extra help messages on warnings and errors")

    (options, args) = parser.parse_args()

    logging.basicConfig()
    logging.getLogger().setLevel(LEVELS[options.debug])

    if(len(args) == 1):
        filename = args[0]
    else:
        parser.print_help()
        sys.exit(1)

    fsm = FSMGen.FSMGen()
    fsm.parseDotFile(filename)

    print "Found %d Unique States:" % (len(fsm.getUniqueStates()))
    for i in fsm.getUniqueStates():
        print "    %s" % i

    ## Checks
    if(options.checks):
        ## Check for default states
        try:
            fsm.checkForDefaultState()
        except FSMGen.MissingTransitionsError, info:
            print "\nThe following states may not have all transition cases covered."
            for i in info.states:
                print "    %s" % i
            if(options.long_messages):
                print info.long_message
#        sys.exit(1)

        ## Check for duplicate state transitions
        try:
            fsm.checkForDuplicateTransitions()
        except FSMGen.DuplicateTransitionError, info:
            print info.error_message

    print "Writing Verilog"
    fsm.writeVerilog()
