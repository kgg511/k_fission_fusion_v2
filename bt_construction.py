import py_trees
from behaviors import *
from agent import Agent
from feeding_site import Site

demo_site = Site([5, 5], 1, 10, 10)
basic_agent = Agent(0, [0,0], 1.0, 0.0, 50, object())
at_site_agent = Agent(1, [5, 5], 1.0, 0.0, 50, object(), site=demo_site)
site_selected_agent = Agent(2, [0, 0], 1.0, 0.0, 50, object(), site=demo_site)

def build_bt(agent):
    # Rest subtree
    rest_subtree = py_trees.composites.Sequence("Rest_Root", False, children=[AtSite("AtSite", agent), 
                                                                        HaveGroupNeighbors("Group", agent),
                                                                        Rest("Rest", agent)])
    rest_root = py_trees.decorators.Repeat("Timer", rest_subtree, 10)

    # GoToSite subtree
    goToSite_subtree = py_trees.composites.Sequence("GoToSite_Actions", False, [HaveNeighbors("Neighbors", agent),
                                                                                GoToSite("GoToSite", agent),
                                                                                Flock("Flock_ToSite", agent)])
    goToSite_root = py_trees.composites.Sequence("GoToSite_Root", False, [SiteSelected("SiteSelected", agent),
                                                                        goToSite_subtree])

    # Explore subtree
    explore_root = py_trees.composites.Sequence("Explore Root", False, [QueryForSites("Query", agent),
                                                                        Flock("Flock_Explore", agent)])

    # actual root
    root = py_trees.composites.Selector("Root", False, children=[rest_root, goToSite_root, explore_root])

    return py_trees.trees.BehaviourTree(root=root)
    
