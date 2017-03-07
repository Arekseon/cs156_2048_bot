"""Implement Agents and Environments (Chapters 1-2).

The class hierarchies are as follows:

Object ## A physical object that can exist in an environment
    Agent
        Wumpus
        RandomAgent
        ReflexVacuumAgent
        ...
    Dirt
    Wall
    ...
    
Environment ## An environment holds objects, runs simulations
    XYEnvironment
        VacuumEnvironment
        WumpusEnvironment

EnvFrame ## A graphical representation of the Environment

"""

#import utils
import random, copy, time, sys
from random import randint
grid_size = 10
try: 
    from termcolor import colored
    with_colors = True
except:
    with_colors = False
color_code = {  "0":"white",
                "2":"white",
                "4":"grey",
                "8":"green",
                "16":"yellow",
                "32":"blue",
                "64":"red",
                "128":"cyan",
                "256":"red",
                "512":"green",
                "1024":"blue",
                "2048":"white"
    
    }
#______________________________________________________________________________

class Object:
    """This represents any physical object that can appear in an Environment.
    You subclass Object to get the objects you want.  Each object can have a
    .__name__  slot (used for output only)."""
    def __repr__(self):
        return '<%s>' % getattr(self, '__name__', self.__class__.__name__)

    def is_alive(self):
        """Objects that are 'alive' should return true."""
        return hasattr(self, 'alive') and self.alive

    def display(self, canvas, x, y, width, height):
        """Display an image of this Object on the canvas."""
        pass

class Agent(Object):
    """An Agent is a subclass of Object with one required slot,
    .program, which should hold a function that takes one argument, the
    percept, and returns an action. (What counts as a percept or action
    will depend on the specific environment in which the agent exists.) 
    Note that 'program' is a slot, not a method.  If it were a method,
    then the program could 'cheat' and look at aspects of the agent.
    It's not supposed to do that: the program can only look at the
    percepts.  An agent program that needs a model of the world (and of
    the agent itself) will have to build and maintain its own model.
    There is an optional slots, .performance, which is a number giving
    the performance measure of the agent in its environment."""

    def __init__(self):
        def program(percept):
            return raw_input('Percept=%s; action? ' % percept)
        self.program = program
        self.alive = True

def TraceAgent(agent):
    """Wrap the agent's program to print its input and output. This will let
    you see what the agent is doing in the environment."""
    old_program = agent.program
    def new_program(percept):
        action = old_program(percept)
        print '%s perceives %s and does %s' % (agent, percept, action)
        return action
    agent.program = new_program
    return agent

#______________________________________________________________________________

class TableDrivenAgent(Agent):
    """This agent selects an action based on the percept sequence.
    It is practical only for tiny domains.
    To customize it you provide a table to the constructor. [Fig. 2.7]"""
    
    def __init__(self, table):
        "Supply as table a dictionary of all {percept_sequence:action} pairs."
        ## The agent program could in principle be a function, but because
        ## it needs to store state, we make it a callable instance of a class.
        Agent.__init__(self)
        percepts = []
        def program(percept):
            percepts.append(percept)
            action = table.get(tuple(percepts))
            return action
        self.program = program


class RandomAgent(Agent):
    "An agent that chooses an action at random, ignoring all percepts."
    def __init__(self, actions):
        Agent.__init__(self)
        self.program = lambda percept: random.choice(actions)


#______________________________________________________________________________

loc_A, loc_B = (0, 0), (1, 0) # The two locations for the Vacuum world

class ReflexVacuumAgent(Agent):
    "A reflex agent for the two-state vacuum environment. [Fig. 2.8]"

    def __init__(self):
        Agent.__init__(self)
        def program((location, status)):
            if status == 'Dirty': return 'Suck'
            elif location == loc_A: return 'Right'
            elif location == loc_B: return 'Left'
        self.program = program


def RandomVacuumAgent():
    "Randomly choose one of the actions from the vaccum environment."
    return RandomAgent(['Right', 'Left', 'Suck', 'NoOp'])


def TableDrivenVacuumAgent():
    "[Fig. 2.3]"
    table = {((loc_A, 'Clean'),): 'Right',
             ((loc_A, 'Dirty'),): 'Suck',
             ((loc_B, 'Clean'),): 'Left',
             ((loc_B, 'Dirty'),): 'Suck',
             ((loc_A, 'Clean'), (loc_A, 'Clean')): 'Right',
             ((loc_A, 'Clean'), (loc_A, 'Dirty')): 'Suck',
             # ...
             ((loc_A, 'Clean'), (loc_A, 'Clean'), (loc_A, 'Clean')): 'Right',
             ((loc_A, 'Clean'), (loc_A, 'Clean'), (loc_A, 'Dirty')): 'Suck',
             # ...
             }
    return TableDrivenAgent(table)


class ModelBasedVacuumAgent(Agent):
    "An agent that keeps track of what locations are clean or dirty."
    def __init__(self):
        Agent.__init__(self)
        model = {loc_A: None, loc_B: None}
        def program((location, status)):
            "Same as ReflexVacuumAgent, except if everything is clean, do NoOp"
            model[location] = status ## Update the model here
            if model[loc_A] == model[loc_B] == 'Clean': return 'NoOp'
            elif status == 'Dirty': return 'Suck'
            elif location == loc_A: return 'Right'
            elif location == loc_B: return 'Left'
        self.program = program
        
#______________________________________________________________________________

class Environment:
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this. Your Environment will typically need to implement:
        percept:           Define the percept that an agent sees.
        execute_action:    Define the effects of executing an action.
                           Also update the agent.performance slot.
    The environment keeps a list of .objects and .agents (which is a subset
    of .objects). Each agent has a .performance slot, initialized to 0.
    Each object has a .location slot, even though some environments may not
    need this."""

    def __init__(self,):
        self.objects = []; self.agents = []

    object_classes = [] ## List of classes that can go into environment

    def percept(self, agent):
	"Return the percept that the agent sees at this point. Override this."
        abstract

    def execute_action(self, agent, action):
        "Change the world to reflect this action. Override this."
        abstract

    def default_location(self, object):
	"Default location to place a new object with unspecified location."
        return None

    def exogenous_change(self):
	"If there is spontaneous change in the world, override this."
	pass

    def is_done(self):
        "By default, we're done when we can't find a live agent."
        for agent in self.agents:
            if agent.is_alive(): return False
        return True

    def step(self):
	"""Run the environment for one time step. If the
	actions and exogenous changes are independent, this method will
	do.  If there are interactions between them, you'll need to
	override this method."""
	if not self.is_done():
            actions = [agent.program(self.percept(agent)) for agent in self.agents]
            for (agent, action) in zip(self.agents, actions):
                self.execute_action(agent, action)
            self.exogenous_change()

    def run(self, steps=1000):
	"""Run the Environment for given number of time steps."""
	for step in range(steps):
            if self.is_done(): return
            self.step()

    def add_object(self, object, location=None):
	"""Add an object to the environment, setting its location. Also keep
	track of objects that are agents.  Shouldn't need to override this."""
	object.location = location or self.default_location(object)
	self.objects.append(object)
	if isinstance(object, Agent):
            object.performance = 0
            self.agents.append(object)
	return self
    

class XYEnvironment(Environment):
    """This class is for environments on a 2D plane, with locations
    labelled by (x, y) points, either discrete or continuous.  Agents
    perceive objects within a radius.  Each agent in the environment
    has a .location slot which should be a location such as (0, 1),
    and a .holding slot, which should be a list of objects that are
    held """

    def __init__(self, width=10, height=10):
        #update(self, objects=[], agents=[], width=width, height=height)
        self.objects=self.agents=[]
        self.width = width
        self.height = height

    def objects_at(self, location):
        "Return all objects exactly at a given location."
        return [obj for obj in self.objects if obj.location == location]

    def objects_near(self, location, radius):
        "Return all objects within radius of location."
        radius2 = radius * radius
        return [obj for obj in self.objects
                if distance2(location, obj.location) <= radius2]

    def percept(self, agent):
        "By default, agent perceives objects within radius r."
        return [self.object_percept(obj, agent)
                for obj in self.objects_near(agent)]

    def execute_action(self, agent, action):
        if action == 'TurnRight':
            agent.heading = turn_heading(agent.heading, -1)
        elif action == 'TurnLeft':
            agent.heading = turn_heading(agent.heading, +1)
        elif action == 'Forward':
            self.move_to(agent, vector_add(agent.heading, agent.location))
        elif action == 'Grab':
            objs = [obj for obj in self.objects_at(agent.location)
                    if obj.is_grabable(agent)]
            if objs:
                agent.holding.append(objs[0])
        elif action == 'Release':
            if agent.holding:
                agent.holding.pop()
        agent.bump = False

    def object_percept(self, obj, agent): #??? Should go to object?
        "Return the percept for this object."
        return obj.__class__.__name__

    def default_location(self, object):
        return (random.choice(self.width), random.choice(self.height))

    def move_to(object, destination):
        "Move an object to a new location."
        
    def add_object(self, object, location=(1, 1)):
        Environment.add_object(self, object, location)
        object.holding = []
        object.held = None
        self.objects.append(object)

    def add_walls(self):
        "Put walls around the entire perimeter of the grid."
        for x in range(self.width):
            self.add_object(Wall(), (x, 0))
            self.add_object(Wall(), (x, self.height-1))
        for y in range(self.height):
            self.add_object(Wall(), (0, y))
            self.add_object(Wall(), (self.width-1, y))

def turn_heading(self, heading, inc,
                 headings=[(1, 0), (0, 1), (-1, 0), (0, -1)]):
    "Return the heading to the left (inc=+1) or right (inc=-1) in headings."
    return headings[(headings.index(heading) + inc) % len(headings)]  

#______________________________________________________________________________
## Vacuum environment 

class TrivialVacuumEnvironment(Environment):
    """This environment has two locations, A and B. Each can be Dirty or Clean.
    The agent perceives its location and the location's status. This serves as
    an example of how to implement a simple Environment."""

    def __init__(self):
        Environment.__init__(self)
        self.status = {loc_A:random.choice(['Clean', 'Dirty']),
                       loc_B:random.choice(['Clean', 'Dirty'])}
        
    def percept(self, agent):
        "Returns the agent's location, and the location status (Dirty/Clean)."
        return (agent.location, self.status[agent.location])

    def execute_action(self, agent, action):
        """Change agent's location and/or location's status; track performance.
        Score 10 for each dirt cleaned; -1 for each move."""
        if action == 'Right':
            agent.location = loc_B
            agent.performance -= 1
        elif action == 'Left':
            agent.location = loc_A
            agent.performance -= 1
        elif action == 'Suck':
            if self.status[agent.location] == 'Dirty':
                agent.performance += 10
            self.status[agent.location] = 'Clean'
        print("performance of {} is {}".format(agent.__name__, agent.performance))

    def default_location(self, object):
        "Agents start in either location at random."
        return random.choice([loc_A, loc_B])


class env_2048(Environment):
    """This environment has two locations, A and B. Each can be Dirty or Clean.
    The agent perceives its location and the location's status. This serves as
    an example of how to implement a simple Environment."""

    def __init__(self):
        Environment.__init__(self)
        self.grid = get_empty_grid()
        # print self.grid
        self.grid = add_random_cell(self.grid)
        # print self.grid
        self.grid = add_random_cell(self.grid)
        # print self.grid


        
    def percept(self, agent):
        "Returns the agent's location, and the location status (Dirty/Clean)."
        return (self.grid)

    def execute_action(self, agent, action):
        """Change agent's location and/or location's status; track performance.
        Score 10 for each dirt cleaned; -1 for each move."""

        if action == 'R':
            self.grid = merge_right(self.grid)
        elif action == 'L':
            self.grid = merge_left(self.grid)
        elif action == 'U':
            self.grid = merge_up(self.grid)
        elif action == 'D':
            self.grid = merge_down(self.grid)
        
        clear_screen()
        self.grid = add_random_cell(self.grid)
        print_grid(self.grid)
        time.sleep(0.01)
        # elif action == 'Suck':
        #     if self.status[agent.location] == 'Dirty':
        #         agent.performance += 10
        #     self.status[agent.location] = 'Clean'
        # print("performance of {} is {}".format(agent.__name__, agent.performance))

    def default_location(self, object):
        "Agents start in either location at random."
        return 0#random.choice([loc_A, loc_B])

    def is_done(self):
        return check_if_win(self.grid) or check_for_lose(self.grid)


def merge_up(grid):
    new_grid =  get_empty_grid()
    for y in xrange(grid_size):
        non_emprty_spot = 0
        can_merge = False
        for x in xrange(grid_size):
            if (not grid[x][y] == 0):
                if non_emprty_spot == 0:
                    new_grid[non_emprty_spot][y] = grid[x][y]
                    non_emprty_spot+=1
                    can_merge = True
                else:
                    if new_grid[non_emprty_spot-1][y] == grid[x][y] and can_merge:
                        new_grid[non_emprty_spot-1][y]*=2
                        can_merge = False
                    else:
                        new_grid[non_emprty_spot][y] = grid[x][y]
                        non_emprty_spot+=1   
    return new_grid

def merge_left(grid):
    rotated_grid = rorate_grid_n_times(grid, 1)
    merged_grid = merge_up(rotated_grid)
    rotated_grid = rorate_grid_n_times(merged_grid, 3)
    return rotated_grid

def merge_down(grid):
    rotated_grid = rorate_grid_n_times(grid, 2)
    merged_grid = merge_up(rotated_grid)
    rotated_grid = rorate_grid_n_times(merged_grid, 2)
    return rotated_grid

def merge_right(grid):
    rotated_grid = rorate_grid_n_times(grid, 3)
    merged_grid = merge_up(rotated_grid)
    rotated_grid = rorate_grid_n_times(merged_grid, 1)
    return rotated_grid



def get_empty_grid():
    grid = []
    for x in xrange(grid_size):
        c = []
        for y in xrange(grid_size):
            c.append(0)
        grid.append(c)
    return  grid

def rorate_grid_n_times(grid, n):
    rotated_grid = grid
    for i in xrange(n):
        rotated_grid = rotate_grid_clockwise(rotated_grid)
    return rotated_grid

def rotate_grid_clockwise(grid):
    new_grid = get_empty_grid()
    for x in xrange(grid_size):
        for y in xrange(grid_size):
            new_grid[y][grid_size-1-x] = grid[x][y]
    return new_grid

def add_random_cell(grid):
    added = False
    while not added:
        x = randint(0,grid_size-1)
        y = randint(0,grid_size-1)
        number = random.choice([2,4])
        if grid[x][y] == 0:
            grid[x][y] = number
            added = True
    return grid

def print_grid(grid, color_code=color_code):
    for line in grid:
        to_print = ""
        for number in line:
            if with_colors:
                colored_number = colored(number, color_code["{}".format(number)])
            else:
                colored_number = number
            if number == 0:
                colored_number = " "
            to_print = "{}{}{}".format(to_print, colored_number, " "*(6 - len(str(number))))
        print to_print



def clear_screen():
    """Clear screen, return cursor to top left"""
    sys.stdout.write('\033[2J')
    sys.stdout.write('\033[H')
    sys.stdout.flush()

def check_if_win(grid):
    for x in xrange(grid_size):
        for y in xrange(grid_size):
            if grid[x][y] == 2048:
                return True
    return False

def check_for_lose(grid):
    return (grid == merge_left(grid)) and (grid == merge_up(grid)) and (grid == merge_down(grid)) and (grid == merge_right(grid)) 
        
def check_fo_valid_move(grid, new_grid):
    return not grid == new_grid


#______________________________________________________________________________

class random_2048_agent(Agent):
    __name__ = "random_2048_agent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            return random.choice(["R","L","U","D"])
        self.program = program

#______________________________________________________________________________

class SimpleReflexAgent(Agent):
    """This agent takes action based solely on the percept. [Fig. 2.13]"""
    __name__ = "SimpleReflexAgent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            location, location_status = percept
            if location_status == 'Dirty':
                return 'Suck'
            if location == loc_A:
                return 'Right'
            else:
                return 'Left'
        self.program = program

class ReflexAgentWithState(Agent):
    """This agent takes action based on the percept and state. [Fig. 2.16]"""

    def __init__(self, rules, udpate_state):
        Agent.__init__(self)
        state, action = None, None
        def program(percept):
            state = update_state(state, action, percept)
            rule = rule_match(state, rules)
            action = rule.action
            return action
        self.program = program

def rule_match(state, rules):
    "Find the first rule that matches state."
    for rule in rules:  
        if rule.matches(state):
            return rule


#______________________________________________________________________________

def compare_agents(EnvFactory, AgentFactories, n=10, steps=1000):
    """See how well each of several agents do in n instances of an environment.
    Pass in a factory (constructor) for environments, and several for agents.
    Create n instances of the environment, and run each agent in copies of 
    each one for steps. Return a list of (agent, average-score) tuples."""
    envs = [EnvFactory() for i in range(n)]
    return [(A, test_agent(A, steps, copy.deepcopy(envs))) 
            for A in AgentFactories]

def test_agent(AgentFactory, steps, envs):
    "Return the mean score of running an agent in each of the envs, for steps"
    total = 0
    for env in envs:
        agent = AgentFactory()
        env.add_object(agent)
        env.run(steps)
        total += agent.performance
    return float(total)/len(envs)

#______________________________________________________________________________

if __name__ == "__main__":
    e = env_2048() 
    

    e.add_object(random_2048_agent())
    e.run(1000)
    


    # overall_performance = test_agent(SimpleReflexAgent, 5, envs)

    # print("\nOverall performance of SimpleReflexAgent is {}".format(overall_performance))