Intro
=====
Tizzy is a Finite State Machine generator for Verilog.  It accepts a subset of
the Graphviz dot syntax as input and generates synthesizable Verilog RTL.

Why Graphviz dot format?
    1) Graphviz viewers are open source
    2) The input is just a text file
    3) Automatic documentation

The name:
    Tizzy = A state of agitation.  That sounds like a state machine to me.


Syntax
======
The basic syntax used to describe state transitions:
    STATE -> STATE_NEXT [label='affector_signal'];
