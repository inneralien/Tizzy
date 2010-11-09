Copyright (c) RTLCores LLC. 2010

Intro
=====
Tizzy is a Finite State Machine generator for Verilog.  It accepts a subset of
the Graphviz dot syntax as input and generates synthesizable Verilog RTL.

Why Graphviz dot format?
    1. Graphviz viewers are open source
    2. The input is just a text file
    3. Automatic documentation

The name:
    Tizzy = *A state of agitation.*  (That sounds like a state machine to me.)

Transition Syntax
=================
The basic syntax used to describe state transitions:
    STATE -> STATE_NEXT [label='affector_signal'];

Usage
=====
::

    $ ./tizzy.py --help
    Usage: tizzy.py <options> [filename]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -d DEBUG, --debug=DEBUG
                            Run in special debug mode. Valid options are debug,
                            info, warning, error, critical
      -n, --nochecks        Do not run error checking routines
      -l, --long_messages   Print out extra help messages on warnings and errors
      -o OUTPUT_FILE, --output=OUTPUT_FILE
                            Write output to a file instead of stdout

Example
=======
The file example_fsm.dot contains the following directed graph representation
of a state machine:

::

    digraph example_fsm
    {
        label = "Example Finite State Machine";
        stIDLE -> stIDLE;
        stIDLE -> stPIPE1 [label = "din_rdy"];
        stPIPE1 -> stPIPE2;
        stPIPE2 -> stLOAD_NEXT;
        stLOAD_NEXT -> stLOAD_DOUT [label = "done"];
        stLOAD_NEXT -> stPIPE1
        stLOAD_DOUT -> stIDLE;
    }

To convert this to verilog you would issue the following commands:

::

    $ ./tizzy.py -o example_fsm.v example_fsm.dot 
    Found 5 Unique States:
        stIDLE
        stPIPE1
        stPIPE2
        stLOAD_NEXT
        stLOAD_DOUT
    Writing Verilog: example_fsm.v

Without the -o option the Verilog output would go to stdout. All the other
messages all go to stderr.
