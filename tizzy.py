#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from optparse import OptionParser
import os
import sys
import FSMGen
import logging

__author__        = "Tim Weaver"
__copyright__     = "Copyright (c) Very White Atom Design, 2010"
__creation_date__ = "Thu Sep  2 09:40:29 PDT 2010"
__version__       = 'v0.1.1'
__disclaimer__    = 'Not responsible...Use at your own risk'

if __name__ == '__main__':
    LEVELS = {  'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL,
            }

    parser = OptionParser(usage="%prog <options> [filename]", version=__version__)
    parser.add_option("-d", "--debug",
                        dest="debug",
                        default='error',
                        help="Run in special debug mode. Valid options are debug, info, warning, error, critical")
    parser.add_option("-n", "--nochecks",
                        default=True,
                        action='store_false',
                        dest="nochecks",
                        help="Do not run error checking routines")
    parser.add_option("-l", "--long_messages",
                        default=False,
                        action='store_true',
                        dest="long_messages",
                        help="Print out extra help messages on warnings and errors")
    parser.add_option("-o", "--output",
                        dest="output_file",
                        help="Write output to a file instead of stdout")

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

    sys.stderr.write("Found %d Unique States:\n" % (len(fsm.getUniqueStates())))
    for i in fsm.getUniqueStates():
        sys.stderr.write("    %s\n" % i)

    ## Checks
    if(options.nochecks):
        ## Check for default states
        try:
            fsm.checkForDefaultState()
        except FSMGen.MissingTransitionsError, info:
            sys.stderr.write("\nThe following states may not have all transition cases covered.\n")
            for i in info.states:
                sys.stderr.write("    %s\n" % i)
            if(options.long_messages):
                sys.stderr.write(info.long_message)

        ## Check for duplicate state transitions
        try:
            fsm.checkForDuplicateTransitions()
        except FSMGen.DuplicateTransitionError, info:
            sys.stderr.write(info.error_message)

    if(options.output_file is not None):
        (root, ext) = os.path.splitext(options.output_file)
        include_filename = root+".vh"
    else:
        include_filename = None

    sys.stderr.write("Writing Verilog: %s\n" % options.output_file)

    fsm.writeVerilog(__version__, options.output_file, include_filename)
#    fsm.writeIncludeFile(__version__, include_filename)
