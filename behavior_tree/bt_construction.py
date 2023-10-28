import py_trees
from behaviors import *
from agent import Agent
from feeding_site import Site

demo_site = Site([5, 5], 1, 10, 10)
basic_agent = Agent(0, [0,0], 1.0, 0.0, 50, object())
at_site_agent = Agent(1, [5, 5], 1.0, 0.0, 50, object(), site=demo_site)
site_selected_agent = Agent(2, [0, 0], 1.0, 0.0, 50, object())

root = py_trees.composites.Selector(name="Root")

# Rest subtree
rest_root = py_trees.composites.Sequence(name="Rest_Root", children=[AtSite(name="AtSite", agent=basic_agent)])
