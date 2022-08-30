#Author: Elias Rosenberg
#Date: November 9th, 2021
#Purpose: Change the original maze class from PA2 to create a random sequence of steps to be given to the robot when running the maze
#Not actually sure if I had to do this, but the lab description describes the robot's path as 'chosen at random' so I thought
#I would follow that description.


from random import random
import random

# Altered_Maze.py
#  original version by db, Fall 2017
#  Feel free to modify as desired.

# Maze objects are for loading and displaying mazes, and doing collision checks.
#  They are not a good object to use to represent the state of a robot mazeworld search
#  problem, since the locations of the walls are fixed and not part of the state;
#  you should do something else to represent the state. However, each Mazeworldproblem
#  might make use of a (single) maze object, modifying it as needed
#  in the process of checking for legal moves.

# Test code at the bottom of this file shows how to load in and display
#  a few maze data files (e.g., "maze1.maz", which you should find in
#  this directory.)

#  the order in a tuple is (x, y) starting with zero at the bottom left

# Maze file format:
#    # is a wall
#    . is a floor
# the command \robot x y adds a robot at a location. The first robot added
# has index 0, and so forth.


#Takes.maz files that are represent ascii mazes, except the dots that used to represent tiles are now letters that
#represent the possible color tiles.

class Maze:

    # internal structure:
    #   self.walls: set of tuples with wall locations
    #   self.width: number of columns
    #   self.rows

    def __init__(self, mazefilename):

        self.robotloc = []
        # read the maze file into a list of strings
        f = open(mazefilename)
        lines = []
        for line in f:
            line = line.strip()
            # ignore blank limes
            if len(line) == 0:
                pass
            elif line[0] == "\\":
                #print("command")
                # there's only one command, \robot, so assume it is that
                parms = line.split()
                x = int(parms[1])
                y = int(parms[2])
                self.robotloc.append(x)
                self.robotloc.append(y)
            else:
                lines.append(line)
        f.close()

        self.width = len(lines[0])
        self.height = len(lines)

        self.map = list("".join(lines))



    def index(self, x, y):
        return (self.height - y - 1) * self.width + x


    # returns True if the location is a floor
    def is_floor(self, x, y):
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False

        return self.map[self.index(x, y)] != "#"


    def has_robot(self, x, y):
        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False

        for i in range(0, len(self.robotloc), 2):
            rx = self.robotloc[i]
            ry = self.robotloc[i + 1]
            if rx == x and ry == y:
                return True

        return False


    # function called only by __str__ that takes the map and the
    #  robot state, and generates a list of characters in order
    #  that they will need to be printed out in.
    def create_render_list(self):
        #print(self.robotloc)
        renderlist = list(self.map)

        robot_number = 0
        for index in range(0, len(self.robotloc), 2):

            x = self.robotloc[index]
            y = self.robotloc[index + 1]

            renderlist[self.index(x, y)] = robotchar(robot_number)
            robot_number += 1

        return renderlist

    #chooses the colors sensed by the robot in n moves
    def create_sequence(self, n_moves):
        sequence = []  # sequence of random moves
        visited = []

        for i in range(0, n_moves):  # for the number of steps we want the robot to take
            curr_x = self.robotloc[0]  # get its current x coordinate
            curr_y = self.robotloc[1] # get its current y coordinate

            new_x = curr_x #placeholder for the new x coord
            new_y = curr_y #placeholder for the new y coord
            print("robot loc: "+ str(self.robotloc[0]) + ", " + str(self.robotloc[0]))

            rand_direction = self.choose_direction()
            if rand_direction == 'N':
                new_y = new_y + 1
                #print('N')
            if rand_direction == 'S':
                new_y = new_y - 1
                #print('S')
            if rand_direction == 'E':
                new_x = new_x + 1
                #print('E')
            if rand_direction == 'W':
                new_x = new_x - 1
                #print('W')

            if self.is_floor(new_x, new_y) and (new_x, new_y) not in visited:  # if the move is legal update the robot's position
                self.robotloc[0] = new_x
                self.robotloc[1] = new_y
                print("new robot location is: " + str(curr_x) + ", " + str(curr_y))
                visited.append((new_x, new_y))
            else:
                print("illegal move, searching for another possible move")
                self.stay()

            color = self.map[self.index(curr_x, curr_y)]
            sequence.insert(i, (curr_x, curr_y, color))

        return sequence


    def choose_direction(self): #returns a random direction uniformly from north, south, east, or west
        directions = ['N', 'S', 'E', 'W'] #possible moves for the robot
        direction = random.choice(directions)

        return direction


    def find_legal_move(self): #sees if a next move is legal, and returns a random possible next move
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        possible_moves = []
        for move in moves:
            if self.is_floor((self.robotloc[0] + move[0]), (self.robotloc[1] + move[1])):
                possible_moves.append(move)

        if len(possible_moves) == 0:
            self.stay()
        else:
            return random.choice(possible_moves)


    def stay(self): #if the robot can't find any legal moves, just stay in place
        self.robotloc = self.robotloc

    def __str__(self):

        # render robot locations into the map
        renderlist = self.create_render_list()

        # use the renderlist to construct a string, by
        #  adding newlines appropriately

        s = ""
        for y in range(self.height - 1, -1, -1):
            for x in range(self.width):
                s+= renderlist[self.index(x, y)]

            s += "\n"

        return s


def robotchar(robot_number):
    return chr(ord("R") + robot_number)


# Some test code

if __name__ == "__main__":
    test_maze1 = Maze("maze1.maz")
    print(test_maze1)
    sequence = test_maze1.create_sequence(10)
    print(sequence)
