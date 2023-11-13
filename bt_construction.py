import py_trees
from behaviors import *
from agent import Agent
from feeding_site import Site

# USED FOR DEBUGGING
demo_site = Site([5, 5], 1, 10, 10)
basic_agent = Agent(0, [0,0], 1.0, 0.0, 50, object())
at_site_agent = Agent(1, [5, 5], 1.0, 0.0, 50, object(), site=demo_site)
site_selected_agent = Agent(2, [0, 0], 1.0, 0.0, 50, object(), site=demo_site)
has_neighbor_agent = Agent(3, [0, 0], 1.0, 0.0, 0.0, object(), neighbors=[1, 2], group_neighbors=None)
has_group_neighbor_agent = Agent(4, [0, 0], 1.0, 0.0, 0.0, object(), neighbors=[0, 1, 2], group_neighbors=[0])

test_behavior_fail = HaveGroupNeighbors("TEST_FAIL", has_neighbor_agent)
test_behavior_success = HaveGroupNeighbors("TEST_SUCCESS", has_group_neighbor_agent)

test_success1 = HaveNeighbors("TEST_SUCCESS1", has_neighbor_agent)
test_success2 = HaveNeighbors("TEST_SUCCESS2", has_group_neighbor_agent)

print(test_behavior_fail.update())
print(test_behavior_success.update())

print(test_success1.update())
print(test_success2.update())

def build_bt(agent):
    # Rest subtree
    rest_root = py_trees.composites.Sequence("Rest_Root", False, children=[AtSite("AtSite", agent), 
                                                                        HaveGroupNeighbors("Group", agent),
                                                                        TimesUp("Timer", agent),
                                                                        Rest("Rest", agent)])
    # rest_root = py_trees.decorators.Repeat("Timer", rest_subtree, 10)

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
    
