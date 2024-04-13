from py_trees.common import Status
from py_trees.behaviour import Behaviour
from World.config import *
from math import floor
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
# TODO: merge Flock and Query for Sites?
class Flock(AgentBehavior):
    def __init__(self, name, agent, attr_factor=1.0, diff_factor=1.0):
        super().__init__(name, agent)
        self.attr_factor = attr_factor
        self.diff_factor = diff_factor

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def initialise(self) -> None:
        if self.agent.timer == 0:
            self.agent.timer = AGENT_REST_TIMER
            print(f"Timer reset on agent{self.agent.id}")
        return super().initialise()
    
    def update(self) -> Status:
        while self.agent.timer > 0: # essentially "IsBored"
            if len(self.agent.neighbors) <= 0:
                print(f"Agent {self.agent.id} has no neighbors, aborting {self.name}\n")
                return Status.FAILURE
            self.agent.repulse_move(self.agent.neighbors, None, attr_factor=self.attr_factor, diff_factor = self.diff_factor)
            self.agent.random_walk(potency=10.0)
            self.agent.timer -= 1
            #print(f"{self.name} is running on Agent {self.agent.id}\n")
            return Status.RUNNING
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
        
        dx += (self.agent.site.pos - self.agent.pos) * 1

        self.agent.pos += (dx * DT * AGENT_SITE_ATTRACTION)
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
                    if self.agent.sim.agents[neighbor].site.is_available():
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
    
class Graze(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        self.agent.hunger += 2
        self.agent.site.resource_count -= 1
        self.agent.timer -= 1
        dx = self.agent.site.pos - self.agent.pos
        self.agent.pos += dx * DT
        #print(f"graze ticked by agent {self.agent.id}\n")
        return Status.SUCCESS
    
class Explore(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        self.agent.random_walk()
        return Status.SUCCESS
    
class Rest(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)
    
    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        # stay in place until neighbors in range
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
            if self.agent.site.is_available():
                #print(f"{self.agent.id} is at site\n")
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

class IsBored(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        #print(f"IsBored ticked on agent{self.agent.id}")
        if self.agent.timer > 0:
            return Status.FAILURE
        #print(f"Agent: {self.agent.id} is bored\n")
        return Status.SUCCESS

class IsHungry(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self.agent.hunger < MAX_HUNGER // 2:
            return Status.SUCCESS
        return Status.FAILURE
    
class IsSatisfied(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)
    
    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        if self.agent.hunger > floor(MAX_HUNGER * 0.75):
            return Status.SUCCESS
        return Status.FAILURE
