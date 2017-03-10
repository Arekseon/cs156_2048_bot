import random, copy, time, sys, collections
from random import randint


#Define those two variables if you want
PLAY_UNTIL = 32768*32768
GRID_SIZE = 16
DELAY = 0.001

#functional constant, better don't change
INFO_LINES = 5 + GRID_SIZE
try: 
    from termcolor import colored
    with_colors = True
except:
    with_colors = False
color_code = {  "0":"white",
                "2":"white",
                "4":"blue",
                "8":"green",
                "16":"yellow",
                "32":"blue",
                "64":"red",
                "128":"cyan",
                "256":"red",
                "512":"green",
                "1024":"blue",
                "2048":"white",
                "4096":"blue",
                "8192":"red",
                "16384":"cyan",
                "32768":"red"  
    }
action_list = ["R","L","U","D"]
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
    
#______________________________________________________________________________
## 2048 Environment

class env_2048(Environment):
    """This environment has two locations, A and B. Each can be Dirty or Clean.
    The agent perceives its location and the location's status. This serves as
    an example of how to implement a simple Environment."""

    def __init__(self, Sound_of_silence=False):
        Environment.__init__(self)
        self.Sound_of_silence = Sound_of_silence
        self.grid = get_empty_grid()
        self.score = 0
        self.steps = 0
        self.highest_number = 0
        self.grid = add_random_cell(self.grid)
        self.grid = add_random_cell(self.grid)
        if not Sound_of_silence:
            print("FIRST GRID")
            print_grid(self.grid)
            print("Score: 0")
            print("Steps: 0")
            print("Highest number: 0")
            print("Last move: ")
            time.sleep(DELAY)


        
    def percept(self, agent):
        "Returns the agent's location, and the location status (Dirty/Clean)."
        return (self.grid)

    def execute_action(self, agent, action):
        """Change agent's location and/or location's status; track performance.
        Score 10 for each dirt cleaned; -1 for each move."""
        self.grid, move_score = merge_on_action(self.grid, action)
        self.score+=move_score
        self.steps+=1
        self.highest_number = get_highest_number(self.grid)
        if check_if_grid_has_emprty_spots(self.grid):
            self.grid = add_random_cell(self.grid)

        if not self.Sound_of_silence:
            clean_n_lines_on_screen(INFO_LINES)
            print("Agent: {}".format(agent.__name__))
            print_grid(self.grid)
            print("Score: {}".format(self.score))
            print("Steps: {}".format(self.steps))
            print("Highest number: {}".format(self.highest_number))
            print("Last move: {}".format(action))
            time.sleep(DELAY)
        

    def default_location(self, object):
        "Agents start in either location at random."
        return 0

    def is_done(self):
        win = check_if_win(self.grid)
        lose = check_if_lose (self.grid) 
        if not self.Sound_of_silence: 
            if win:
                print("You won, bitch!")
            if lose:
                print("You lost, bitch!")
        return win or lose

def check_if_grid_has_emprty_spots(grid):
    for x in xrange(GRID_SIZE):
        for y in xrange(GRID_SIZE):
            if grid[x][y] == 0:
                return True
    return False


def get_highest_number(grid):
    highest_number = 0
    for x in xrange(GRID_SIZE):
        for y in xrange(GRID_SIZE):
            if grid[x][y]> highest_number:
                highest_number = grid[x][y]
    return highest_number

def merge_on_action(grid, action):
    if action == 'R':
        return  merge_right(grid)
    elif action == 'L':
        return  merge_left(grid)
    elif action == 'U':
        return  merge_up(grid)
    elif action == 'D':
        return  merge_down(grid)
    else:
        return False

def merge_up(grid):
    score_count = 0
    new_grid =  get_empty_grid()
    for y in xrange(GRID_SIZE):
        non_emprty_spot = 0
        can_merge = False
        for x in xrange(GRID_SIZE):
            if (not grid[x][y] == 0):
                if non_emprty_spot == 0:
                    new_grid[non_emprty_spot][y] = grid[x][y]
                    non_emprty_spot+=1
                    can_merge = True
                else:
                    if new_grid[non_emprty_spot-1][y] == grid[x][y] and can_merge:
                        new_grid[non_emprty_spot-1][y]*=2
                        score_count+= new_grid[non_emprty_spot-1][y]
                        can_merge = False
                    else:
                        new_grid[non_emprty_spot][y] = grid[x][y]
                        non_emprty_spot+=1   
    return new_grid, score_count

def merge_left(grid):
    rotated_grid = rorate_grid_n_times(grid, 1)
    merged_grid, score_count = merge_up(rotated_grid)
    rotated_grid = rorate_grid_n_times(merged_grid, 3)
    return rotated_grid, score_count

def merge_down(grid):
    rotated_grid = rorate_grid_n_times(grid, 2)
    merged_grid, score_count = merge_up(rotated_grid)
    rotated_grid = rorate_grid_n_times(merged_grid, 2)
    return rotated_grid, score_count

def merge_right(grid):
    rotated_grid = rorate_grid_n_times(grid, 3)
    merged_grid, score_count = merge_up(rotated_grid)
    rotated_grid = rorate_grid_n_times(merged_grid, 1)
    return rotated_grid, score_count



def get_empty_grid():
    grid = []
    for x in xrange(GRID_SIZE):
        c = []
        for y in xrange(GRID_SIZE):
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
    for x in xrange(GRID_SIZE):
        for y in xrange(GRID_SIZE):
            new_grid[y][GRID_SIZE-1-x] = grid[x][y]
    return new_grid

def add_random_cell(grid):
    added = False
    while not added:
        x = randint(0,GRID_SIZE-1)
        y = randint(0,GRID_SIZE-1)
        number = random.choice([2,4])
        if grid[x][y] == 0:
            grid[x][y] = number
            added = True
    return grid

def print_grid(grid, color_code=color_code):
    for line in grid:
        to_print = ""
        for number in line:
            if with_colors and (str(number) in color_code):
                colored_number = colored(number, color_code["{}".format(number)])
            else:
                colored_number = number
            if number == 0:
                colored_number = " "
            to_print = "{}{}{}".format(to_print, colored_number, " "*(6 - len(str(number))))
        print to_print

def clean_n_lines_on_screen(n):
    for i in xrange(n):
        sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line

def clear_screen():
    """Clear screen, return cursor to top left"""
    sys.stdout.write('\033[2J')
    sys.stdout.write('\033[H')
    sys.stdout.flush()

def check_if_win(grid):
    for x in xrange(GRID_SIZE):
        for y in xrange(GRID_SIZE):
            if grid[x][y] == PLAY_UNTIL:
                return True
    return False

def check_if_lose(grid):
    for action in action_list:
        potential_grid, _ = merge_on_action(grid, action)
        if not grid == potential_grid:
            return False
    # print "looser"
    return True 

def check_for_valid_action(grid, action):
    # print grid
    new_grid,_ = merge_on_action(grid, action)
    # print new_grid
    return check_fo_valid_move(grid, new_grid)
        
def check_fo_valid_move(grid, new_grid):
    return not grid == new_grid


#__________________________________AGENTS____________________________________________

class random_2048_agent(Agent):
    __name__ = "random_2048_agent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            return random.choice(action_list)
        self.program = program

class random_2048_agent_with_validity_check(Agent):
    __name__ = "random_2048_agent_with_validity_check"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            grid = percept
            action = random.choice(action_list)
            while not check_fo_valid_move(grid, merge_on_action(grid, action)):
                action = random.choice(action_list)
            return action
        self.program = program

class greedy_2048_agent(Agent):
    __name__ = "greedy_2048_agent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            grid = percept
            return random.choice(get_best_greedy_actions(grid))
        self.program = program

class two_steps_greedy_2048_agent(Agent):
    __name__ = "two_steps_greedy_2048_agent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            grid = percept
            first_step_best_actions = get_best_greedy_actions(grid)
            first_step_best_actions = get_valid_moves(grid, first_step_best_actions)
            best_first_step = random.choice(first_step_best_actions)
            best_second_step_score = 0
            for first_step_action in first_step_best_actions:
                first_step_grid,_ = merge_on_action(grid, first_step_action)
                for second_step_action in action_list:
                    _,score = merge_on_action(first_step_grid, second_step_action)
                    if score>best_second_step_score:
                        best_first_step = first_step_action
                        best_second_step_score = score
            return best_first_step
        self.program = program


def get_best_greedy_actions(grid):
    best_actions = []
    best_action_score = 0
    for action in action_list:
        _,score = merge_on_action(grid, action)
        if score > best_action_score:
            best_action_score = score
            best_actions = [action]
        elif score == best_action_score:
            best_actions.append(action)
    random.shuffle(best_actions)
    return best_actions

def get_valid_moves(grid, actions):
    valid_actions = []
    for action in actions:
        if check_for_valid_action(grid, action):
            valid_actions.append(action)
    return valid_actions

class left_corners_2048_agent(Agent):
    __name__ = "left_corners_2048_agent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            grid = percept
            actions = get_valid_moves(grid, ['U','L','D'])
            if len(actions) ==0:
                action = 'R'
            else:
                action = random.choice(actions)
            return action
        self.program = program

class left_corners_greed_2048_agent(Agent):
    __name__ = "left_corners_greed_2048_agent"
    def __init__(self):
        Agent.__init__(self)
        def program(percept):
            grid = percept

            actions = get_best_greedy_actions(grid)
            if 'R' in actions:
                actions.remove('R')
            if len(actions) ==0:
                action = 'R'
            else:
                action = random.choice(actions)
            return action
        self.program = program



#______________________________________________________________________________

def test_2048_agents(AgentFactory, steps, envs):
    print("____________________________________")
    print("Agent: {}".format(AgentFactory.__name__))
    print("Tests run: 0")
    total_score = 0
    highest_numbers = { 0:0,
                        2:0,
                        4:0,
                        8:0,
                        16:0,
                        32:0,
                        64:0,
                        128:0,
                        256:0,
                        512:0,
                        1024:0,
                        2048:0,
                        4096:0,
                        8192:0,
                        16384:0,
                        32768:0}
    counter = 0
    update_lines = 0
    for env in envs:
        agent = AgentFactory()
        env.add_object(agent)
        env.run(steps)
        total_score += env.score
        highest_numbers[env.highest_number]+=1

        counter+=1
        clean_n_lines_on_screen(1+update_lines)
        print("Tests run: {}".format(counter))

        average_score = float(total_score)/counter
        print("Grid size: {}x{}".format(GRID_SIZE, GRID_SIZE))
        print("Average score: {}".format(average_score))
        print("Highest numbers: ")
        update_lines = 3

        sorted_highest_numbers = collections.OrderedDict(sorted(highest_numbers.items()))
        for key, value in sorted_highest_numbers.iteritems():
            if not value == 0:  
                print("{}{} - {} times".format(key," "*(5-len(str(key))) ,value))
                update_lines+=1

def testv(agent, envs): 
    return test_2048_agents(agent, 100000, copy.deepcopy(envs)) 

def watch_agent_in_env(AgentFactory, EnvFactory):
    e = EnvFactory()
    e.add_object(AgentFactory())
    e.run(100000) 
#______________________________________________________________________________

def demo():
    #List of all agents to test
    agents_to_test = [  random_2048_agent, 
                random_2048_agent_with_validity_check,
                greedy_2048_agent,
                two_steps_greedy_2048_agent,
                left_corners_2048_agent,
                left_corners_greed_2048_agent]


    #Run visual test 
    for agent in agents_to_test:
        print("____________________________________")
        watch_agent_in_env(agent, env_2048)
        time.sleep(2)


    #Run massive testings
    envs = [env_2048(Sound_of_silence=True) for i in range(100)]
    for agent in agents_to_test:
            testv(agent, envs)


def demo_one_agent(AgentFactory, times=0, visual=True):
    if visual:
        print("____________________________________")
        watch_agent_in_env(AgentFactory, env_2048)
        time.sleep(2)
    if times !=0:
        envs = [env_2048(Sound_of_silence=True) for i in range(times)]
        testv(AgentFactory, envs)

if __name__ == "__main__":
    clear_screen()
    # demo()
    # demo_one_agent(two_steps_greedy_2048_agent, times=1000)
    demo_one_agent(two_steps_greedy_2048_agent)
