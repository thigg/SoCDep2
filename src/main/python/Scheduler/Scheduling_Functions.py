# Copyright (C) 2015 Siavoosh Payandeh Azad 


def find_schedule_make_span(ag):
    """
    Calculates the makespan of the Scheduling
    :param ag: Architecture Graph
    :return: MakeSpan of the Scheduling
    """
    make_span = 0
    for Node in ag.nodes():
        for Task in ag.node[Node]['PE'].mapped_tasks:
            make_span = max(ag.node[Node]['PE'].scheduling[Task][1], make_span)
    return make_span


################################################################
def clear_scheduling(ag):
    """
    Clears scheduling from PEs, Routers and Links
    :param ag: Architecture Graph
    :return: None
    """
    for node in ag.nodes():
        ag.node[node]['PE'].scheduling = {}
        ag.node[node]['Router'].scheduling = {}
    for link in ag.edges():
        ag.edge[link[0]][link[1]]['Scheduling'] = {}
    return None
