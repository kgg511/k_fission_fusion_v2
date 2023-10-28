from py_trees.common import Status
from py_trees.behaviour import Behaviour

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
        print("Flocking behavior ticked")
        return Status.SUCCESS
    
class GoToSite(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        print("Going to site ticked")
        return Status.SUCCESS
    
class QueryForSites(AgentBehavior):
    def __init__(self, name, agent):
        super().__init__(name, agent)

    def initialise(self) -> None:
        return super().initialise()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)
    
    def update(self) -> Status:
        print("Query behavior ticked")
        # query neighbors (if any) for sites
        # accept or reject site
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
        if self.agent.neighbors or len(self.agent.neighbors) > 0:
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
        if self.agent.group_neighbors or len(self.agent.group_neighbors) > 0:
            return Status.SUCCESS
        return Status.FAILURE
