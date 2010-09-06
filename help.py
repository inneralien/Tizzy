missing_transition_help = """
    What this means is that there won't be an 'else' clause in the
    state transition logic for this state. This could cause the
    default state to be set unexpectedly.
    If a state transition is caused by an affector then there
    should be another state transition back to the same state.

    For Example:
    This state transition has an affector "rdy":
        FIRST -> SECOND [label= "rdy"];
    So there should also be a same-state transition to cover the case where
    "rdy" isn't asserted:
        FIRST -> FIRST;
"""
