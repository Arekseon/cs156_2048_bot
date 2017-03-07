import random, sys, time,tty,termios
from random import randint
grid_size = 8
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
#TODO:
# - fix exit() /sorta solved

class _Getch:
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

def get_arrow():
    inkey = _Getch()
    while(1):
            k=inkey()
            if k!='':break
    if k=='\x1b[A':
            return "U"
    elif k=='\x1b[B':
            return "D"
    elif k=='\x1b[C':
            return "R"
    elif k=='\x1b[D':
            return "L"
    else:
            return "Q"



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

def rorate_grid_n_times(grid, n):
    rotated_grid = grid
    for i in xrange(n):
        rotated_grid = rotate_grid_clockwise(rotated_grid)
    return rotated_grid

def get_empty_grid():
    grid = []
    for x in xrange(grid_size):
        c = []
        for y in xrange(grid_size):
            c.append(0)
        grid.append(c)
    return  grid


def rotate_grid_clockwise(grid):
    new_grid = get_empty_grid()
    for x in xrange(grid_size):
        for y in xrange(grid_size):
            new_grid[y][grid_size-1-x] = grid[x][y]
    return new_grid

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

def add_random_cell(grid):
    added = False
    while not added:
        x = randint(0,grid_size-1)
        y = randint(0,grid_size-1)
        number = random.choice([2,4])
        if grid[x][y] == 0:
            grid[x][y] = number
            added = True



def clear():
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

def get_user_move():
    user_comand = get_arrow()
    # user_comand = raw_input("Your move, bitch[L,R,U,D]:")
    while not ( user_comand in ["L", "R", "U", "D", "l", "r", "u", "d", "q", "Q"] ):
        print("try to use arrows and not {}".format(user_comand))
        user_comand = get_arrow()
        #         
        # user_comand = raw_input("Try again, bitch [L/R/U/D]:")
    return user_comand

def start_game():
    clear()
    current_grid = get_empty_grid()
    print_grid(current_grid,color_code)
    time.sleep(1)
    clear()
    add_random_cell(current_grid)
    add_random_cell(current_grid)
    print_grid(current_grid)
    # user_comand = raw_input("Your move, bitch[L,R,U,D]:")
    win = False
    lose = False
    while not (win or lose):
        action = get_user_move()
        if action == "L" or action == "l":
            new_grid = merge_left(current_grid)
        if action == "R" or action == "r":
            new_grid = merge_right(current_grid)
        if action == "U" or action == "u":
            new_grid = merge_up(current_grid)
        if action == "D" or action == "d":
            new_grid = merge_down(current_grid)
        if action == "Q" or action == "q":
            sys.exit(0)

        lose = check_for_lose(new_grid)
        
        if check_fo_valid_move(current_grid, new_grid):
            win = check_if_win(new_grid)
            
            if lose or win:
                break
            clear()
            add_random_cell(new_grid)
            print_grid(new_grid)
            current_grid = new_grid

    print("You won, bitch!" if win else "You lost, bitch!")


if __name__ == "__main__":
    start_game()
    # main()














