all: run

example_fsm.v:	../example_fsm.dot
	../tizzy.py -o example_fsm.v ../example_fsm.dot
#	cp ../example_fsm.v .

sim:	tb.v example_fsm.v
	iverilog -o sim tb.v example_fsm.v

.PHONY: run
run:	sim
	./sim

.PHONY: clean
clean:
	rm -f example_fsm.v sim *.vcd
