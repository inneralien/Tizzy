/*
 *  A very basic test to make sure all states are exercized
 */

`timescale 1ns/100ps

module tb();
`ifndef D
    `define D #1
`endif

reg         clock;
reg         reset;
reg         din_rdy;
reg         done;
wire [4:0]  state;
wire [4:0]  state_next;

localparam
    stIDLE = 0,
    stPIPE1 = 1,
    stPIPE2 = 2,
    stLOAD_NEXT = 3,
    stLOAD_DOUT = 4;

initial begin
    $dumpfile("out.vcd");
    $dumpvars(0, tb);
end

initial begin
    clock = 1'b0;
    forever clock = #47 ~clock; // 16MHz
end

initial begin
    $display("==========================");
    $display(" Basic State Machine Test");
    $display("==========================");
    reset = 1'b1;
    din_rdy = 1'b0;
    done = 1'b0;

    #1;
    reset_chip;

    repeat(2) @(posedge clock);
    if(state[stIDLE] != 1'b1)
        $display("<%0t> Mismatch in stIDLE: %b", $time, state);
    else
        $display("<%0t> State: %b", $time, state);

        /* Pulse din_rdy */
    @(posedge clock) din_rdy = `D 1'b1;
    @(posedge clock) din_rdy = `D 1'b0;

        /* Check each state */
    @(posedge clock)
        if(state[stPIPE1] != 1'b1)
            $display("<%0t> Mismatch in stPIPE1: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    @(posedge clock)
        if(state[stPIPE2] != 1'b1)
            $display("<%0t> Mismatch in stPIPE2: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    @(posedge clock)
        if(state[stLOAD_NEXT] != 1'b1)
            $display("<%0t> Mismatch in stLOAD_NEXT: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    @(posedge clock)
        if(state[stPIPE1] != 1'b1)
            $display("<%0t> Mismatch in stPIPE1: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    @(posedge clock)
        if(state[stPIPE2] != 1'b1)
            $display("<%0t> Mismatch in stPIPE2: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    done = `D 1'b1;
    @(posedge clock)
        if(state[stLOAD_NEXT] != 1'b1)
            $display("<%0t> Mismatch in stLOAD_NEXT: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    @(posedge clock)
        if(state[stLOAD_DOUT] != 1'b1)
            $display("<%0t> Mismatch in stLOAD_DOUT: %b", $time, state);
        else
            $display("<%0t> State: %b", $time, state);
    repeat(5) @(posedge clock);
    $finish();
end

task reset_chip;
begin
    reset = 1'b1;
    repeat(5) @(posedge clock);
    reset = 1'b0;
end
endtask

example_fsm fsm(
    .clock      (clock),        //I
    .reset      (reset),        //I
    .din_rdy    (din_rdy),      //I
    .done       (done),         //I
    .state      (state),        //O [4:0]
    .state_next (state_next)    //O [4:0]
);

endmodule
