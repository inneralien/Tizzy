missing_transition_help = """
    What this means is that there won't be an 'else' clause in the state
    transition logic for this state. This could cause the default state to be
    set unexpectedly if all cases aren't covered explicitly.
    If a state transition is caused by an affector then there should be another
    state transition that does not have an affector.

    For Example:
    This state transition has an affector "rdy":
        FIRST -> SECOND [label= "rdy"];
    So there should also be another state transition to cover the case where
    "rdy" isn't asserted:
        FIRST -> FIRST;
    or
        FIRST -> SOME_OTHER_STATE;
"""
