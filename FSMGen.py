import sys
import os
import re
import time
import logging
import string
from NullHandler import NullHandler
import help
from vlogTemplate import vlogTemplate
from incTemplate import incTemplate

"""
Reads in a Graphviz .dot file and generates a Verilog state machine based
on some simple rules.

1)  Only one state transitions per line:
        state_name -> next_state_name;
        next_state_name -> next_next_state_name;
    not
        state_name -> next_state_name -> next_next_state_name;

2)  Events that cause state transitions are called "affectors" and are defined
    by .dot labels:
        state_name -> next_state_name [label = "start"];
    These events will generate input ports of the same name as the label.
"""
class StateTransition():
    def __init__(self, state):
        self.state = state
        self.transitions = []

        self.default = None

    def str(self):
        return self.state


class FSMGen():
    def __init__(self):
        self.__title = ""
        self.__unique_states = []
        self.__num_states = 0
        self.__states = {}
        self.__transitions = []
        self.__unique_affectors = []
        self.__default_state = None
        self.__dotfile = None
        self.logger = logging.getLogger("FSMGen")
        h = NullHandler()
        logging.getLogger("FSMGen").addHandler(h)

        self.subs = {   'website':              "https://github.com/inneralien/Tizzy",
                        'dot_filename':         "",
                        'filename':             "",
                        'creation_date':        "",
                        'title':                "",
                        'module_name':          "",
                        'inputs':               "",
                        'msb':                  "",
                        'lsb':                  "",
                        'state_params':         "",
                        'range':                "",
                        'next_state_logic':     "",
                        'state_generator':      "",
                        'state_debug':          "",
        }
        self.longest_state_str = 0

    def getUniqueStates(self):
        return self.__unique_states

    def checkForDefaultState(self):
        """
        If the transition has an affector, check to see if there is
        also a same state transition with no affector.
        """
        self.logger.info("Checking for explicit same-state transitions")
        affector_states = []
        for state in self.__unique_states:
            for trans in self.__states[state].transitions:
                if(trans[1] is None):
                    self.logger.debug("Has same state trans: %s" % (state))
                    has_same_state_trans = True
                    break
                else:
                    has_same_state_trans = False
            if(has_same_state_trans is False):
                affector_states.append(state)

        if(len(affector_states) > 0):
            raise MissingTransitionsError("addSameStateTransition",
                "Some states may not have all transitions covered",
                help.missing_transition_help,
                affector_states)

    def checkForDuplicateTransitions(self):
        """
        Takes a list of StateTransition objects and checks to see
        if there are any duplicate affectors that cause transitions
        from the same current state.  i.e.
            IDLE -> P1 [label='run'];
            IDLE -> P2 [label='run'];
        """
        self.logger.info("Checking for duplicate state transitions")

        state_trans = []
        for t in self.__transitions:
            # Make a string of the three values
            if(t.affector is not None):
                val = t.state + t.state_next + t.affector
            else:
                val = t.state + t.state_next

            if(val in state_trans):
                raise DuplicateTransitionError("checkForDuplicateTransitions",
                    "A duplicate state transition was found\n    %s -> %s" % (t.state, t.state_next),
                    None)
            else:
                state_trans.append(val)

        for i in state_trans:
            if(state_trans.count(i) > 1):
                print "More than once: %s" % i

        if(False):
            raise FSMError("Duplicate Affectors",
                "Attempting multiple state transitions with the same affector")

    def parseDotFile(self, filename):
        """
        The parser is looking for 3 things:
        1) FSM label
            label = "My Fancy State Machine"
        2) State transitions
            IDLE -> PIPE1;
        3) Explicit affectors which cause the state change
            IDLE -> PIPE1 [label = "rdy"];

        Checks:
            1) Same affector used to transition to multiple next states from
            the current state. i.e.
                    IDLE -> P1 [label='run'];
                    IDLE -> P2 [label='run'];
            2) No explicit same-state transition:
                    IDLE -> P1 [label='run'];
                but missing:
                    IDLE -> IDLE;
                The same-state transition will be created automatically.
        """
        re_fsm_name = re.compile(r'^\s*digraph\s*(\w+)')
        re_fsm_label = re.compile(r'^\s*label\s*=\s*\"(.*)\"')
        re_states = re.compile(r'^\s*(\w+)\s*->\s*(\w+)')
        re_affectors = re.compile(r'\[\s*label\s*=\s*\"(.*)\"\s*\]')

        self.subs['dot_filename'] = filename
        f = open(filename, 'r')
        self.__dotfile = f.read()
        f.close()
        file = self.__dotfile.split('\n')
        for line in file:
            st = None

                ## Find FSM Module Name
            m = re_fsm_name.search(line)
            if(m is not None):
                self.__name = m.group(1)
                self.logger.info("Found Module Name: %s" % self.__name)

                ## Find FSM Title
            m = re_fsm_label.search(line)
            if(m is not None):
                self.__title = m.group(1)
                self.logger.info("Found Title: %s" % self.__title)

                ## Find States and Next States
            m_state = re_states.search(line)
            if(m_state is not None):
                state = m_state.group(1)
                if state not in self.__unique_states:
                    self.__unique_states.append(state)
                    self.logger.debug("Adding state: %s" % state)
                    self.__states[state] = StateTransition(state)
                    if(len(state) > self.longest_state_str):
                        self.longest_state_str = len(state)
                    ## Find Transitions
                m_affector = re_affectors.search(line)
                if(m_affector is not None):
                    affector = m_affector.group(1)
                    ## Strip off ~ and ! etc.
                    affector_stripped = re.sub('[~|!()&^]','',affector).split()
                    self.logger.debug("Stripped affectors: '%s'" % affector_stripped)
                    for i in affector_stripped:
                        if(i not in self.__unique_affectors):
                            self.logger.debug("Adding unique affector: '%s'" % i)
                            self.__unique_affectors.append(i)
                else:
                    affector = None

                next_state = m_state.group(2)
                self.logger.debug("Adding transition: %s -> %s (%s)" %  (state, next_state, affector))
                trans = (next_state, affector)
                if(trans in self.__states[state].transitions):
                    raise DuplicateTransitionError("checkForDuplicateTransitions",
                        "A duplicate state transition was found\n    %s -> %s" % (state, next_state),
                        None)
                else:
                    self.__states[state].transitions.append((next_state, affector))

        self.__default_state = self.__unique_states[0]
        self.__num_states = len(self.__unique_states)
        self.logger.debug("State Transitions:")
        for state in self.__unique_states:
            for trans in self.__states[state].transitions:
                self.logger.debug("    %s -> %s %s" % (state, trans[0], trans[1]))

    def getInputPorts(self):
        """
        Creates and returns a string of input ports.
        """
        pass

    def getOutputPorts(self):
        """
        Creates and returns a string of output ports.
        """
        pass

    def genNextStateLogicString(self):
        """
        Returns a string that represents the next state generator Verilog code.
        """
        str = ""
            ## The first state is the default state
        for state in self.__unique_states:
            final_trans = None
            first_trans = None
            other_trans = []

            str  += "        state[%s] :\n" % state

            num_trans = len(self.__states[state].transitions)
            for i in range(num_trans):
                remaining = num_trans - i
                trans = self.__states[state].transitions[i]
                self.logger.debug(remaining)

                if(trans[1] is None):
                    if(final_trans is None):
                        self.logger.debug("Final trans: %r %r" % (trans[0], trans[1]))
                        final_trans = trans
                    else:
                        raise MultipleDefaultTransitionsError('genNextStateLogicString', None, None)
                else:
                    if(first_trans is None):
                        self.logger.debug("First trans: %r %r" % (trans[0], trans[1]))
                        first_trans = trans
                    else:
                        self.logger.debug("Other trans: %r %r" % (trans[0], trans[1]))
                        other_trans.append(trans)

            if(first_trans is not None):
                str += "            if(%s)\n" % first_trans[1]
                str += "                state_next[%s] = 1'b1;\n" % first_trans[0]

            if(other_trans is not None):
                for trans in other_trans:
                    str += "            else if(%s)\n" % trans[1]
                    str += "                state_next[%s] = 1'b1;\n" % trans[0]

            if(final_trans is not None):
                if(num_trans != 1):
                    str += "            else\n"
                str += "                state_next[%s] = 1'b1;\n" % final_trans[0]

        str += "        default:\n"
        str += "            state_next[%s] = 1'b1;" % self.__default_state
        return str

    def genStateGeneratorString(self):
        """
        Returns a string that represents the state generator Verilog code.
        """
        str = ""
        str += "        state <= `D %d'b0;\n" % self.__num_states
        str += "        state[%s] <= `D 1'b1;" % self.__default_state
        return str

    def genStateDebugString(self):
        """
        Returns a string the represents some state debug Verilog code.
        """
#        longest = 0
#        for state in self.__unique_states:
#            str_len = len(state)
#            if(str_len > longest):
#                longest = str_len
        str = ""
        str += "// synthesis translate_off\n"
        str += "// State names for simulation\n"
        str += "reg [79:0] state_string;\n"
        str += "always @(*)\n"
        str += "    case(1'b1)\n"
        for state in self.__unique_states:
            state_str = "state[%s]" % state
            str += '        %s : state_string = "%s";\n' % \
                (state_str.ljust(8+self.longest_state_str), state)
        str += "    endcase\n"
        str += "// synthesis translate_on\n"
        return str

    def fillStringSubs(self):
#        self.subs['creation_date'] = time.strftime("%b %d %Y")
        self.subs['creation_date'] = time.strftime("%d-%b-%Y")
        self.subs['title'] = self.__title
        self.subs['module_name'] = self.__name
        for i in self.__unique_affectors:
            self.subs['inputs'] += "    input   wire %s,\n" % i
        self.subs['msb'] = self.__num_states-1
        self.subs['lsb'] = 0
        for i in range(self.__num_states):
            str = "    %s = %d" % \
                (self.__unique_states[i].ljust(self.longest_state_str), i)
            if(i < self.__num_states-1):
                str += ",\n"
            else:
                str += ";"
            self.subs['state_params'] += str
        self.subs['range'] = self.__num_states
        self.subs['next_state_logic'] = self.genNextStateLogicString()
        self.subs['state_generator'] = self.genStateGeneratorString()
        self.subs['digraph'] = self.__dotfile
        self.subs['state_debug'] = self.genStateDebugString()

    def writeVerilog(self, version, filename=None, include_file=None):
        """
        Writes the verilog using a string template.
        If filename is None then stdout is used.
        """
            # Verilog Filename
        self.subs['version'] = version
        if(filename is None):
            self.subs['filename'] = "STDIO"
        else:
            self.subs['filename'] = filename

            # Include Filename
        if(include_file is None):
            include_file = "states.vh"
        (head, tail) = os.path.split(include_file)
        self.subs['include_file'] = tail

        s = string.Template(vlogTemplate)

        self.fillStringSubs()

        if(filename is None):
            sys.stdout.write(s.safe_substitute(self.subs))
        else:
            f = open(self.subs['filename'], 'w')
            f.write(s.safe_substitute(self.subs))
            f.close()

        self.writeIncludeFile(version, include_file)

    def writeIncludeFile(self, version, filename=None):
        """
        Writes an include file that contains the state parameters.
        """
        sys.stderr.write("Writing include file: %s\n" % filename)
        s = string.Template(incTemplate)
        f = open(filename, 'w')
        f.write(s.safe_substitute(self.subs))
        f.close()

class FSMError(Exception):
    def __init__(self, method_name, error_message, long_message):
        Exception.__init__(self)
        self.method_name = method_name
        self.error_message = error_message
        self.long_message = long_message

class MissingTransitionsError(FSMError):
    def __init__(self, method_name, error_message, long_message, states):
        FSMError.__init__(self, method_name, error_message, long_message)
        self.states = states

class DuplicateTransitionError(FSMError):
    def __init__(self, method_name, error_message, long_message):
        FSMError.__init__(self, method_name, error_message, long_message)

class MultipleDefaultTransitionsError(FSMError):
    def __init__(self, method_name, error_message, long_message):
        FSMError.__init__(self, method_name, error_message, long_message)

