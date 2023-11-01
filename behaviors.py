from py_trees.common import Status
from py_trees.behaviour import Behaviour
from config import *
import numpy as np

class AgentBehavior(Behaviour):
    def __init__(self, name, agent):
        super().__init__(name)
        self.agent = agent # move agent to blackboard as well
        # self.blackboard = self.attach_blackboard_client() # TODO: figure out blackboard

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def initialise(self) -> None:
        return super().initialise()
    
    def update(self) -> Status:
        return super().update()
    
    def set_agent(self, agent):
        self.agent = agent
    
### ACTUAL BEHAVIOR ###
class Flock(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def initialise(self) -> None:
        return super().initialise()
    
    def update(self) -> Status:
        self.agent.repulse_move(self.agent.neighbors, None)
        self.agent.random_walk(potency=1.0)
        return Status.SUCCESS
    
class GoToSite(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        dx = 0
        if self.agent.following != None:
            dx = self.agent.sim.get_agent_pos(self.agent.following) - self.agent.pos # essentially double counting the group leader
        
        dx += self.agent.site.pos - self.agent.pos

        self.agent.pos += (dx * DT)
        return Status.SUCCESS
    
class QueryForSites(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        # query neighbors (if any) for sites
        if len(self.agent.group_neighbors) > 0:
            for neighbor in self.agent.group_neighbors:
                if self.agent.sim.agents[neighbor].site != None:
                    # accept or reject site
                    if np.random.random() > 0.2:
                        self.agent.site = self.agent.sim.agents[neighbor].site
                        self.agent.add_site(self.agent.site)
                        self.agent.following = neighbor
                        return Status.SUCCESS

        for site in self.agent.potential_sites:
            # random chance to actually want to go to site (default set to 50%?)
            if np.random.random() > 0.5:
            # make sure we don't go back to last_known_site so agents can wander away
                viable_sites = list(filter(lambda i: i not in self.agent.last_known_sites, self.agent.potential_sites))
                if len(viable_sites) > 0:
                    self.agent.site = viable_sites[np.random.randint(0, len(viable_sites))]
                    self.agent.add_site(self.agent.site)

        return Status.SUCCESS
    
class Rest(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        dx = self.agent.site.pos - self.agent.pos
        self.agent.pos += dx * DT
        return Status.SUCCESS
    
### CONDITIONS ###

# check if at site
class AtSite(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self.agent.at_site():
            return Status.SUCCESS
        return Status.FAILURE

# check if site is selected
class SiteSelected(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self.agent.site == None:
            return Status.FAILURE
        return Status.SUCCESS

# check if there are neighbors
class HaveNeighbors(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self.agent.neighbors != None:
            if len(self.agent.neighbors) > 0:
                return Status.SUCCESS
        return Status.FAILURE

# check if there are group neighbors
class HaveGroupNeighbors(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self.agent.group_neighbors != None:
            if len(self.agent.group_neighbors) > 0:
                return Status.SUCCESS
        return Status.FAILURE
