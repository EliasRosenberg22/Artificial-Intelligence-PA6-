#Author: Elias Rosenberg
#Date: November 10, 2021
#Purpose: Implement the Forward-Backward algorithm from the textbook to return a probability distribution of a robot's position
#over a certain amount of time-steps (here, a premade, random sequence of moves from Altered-Maze.py)

#* I worked with my friend on the forward-backward algorithm and the elements needed to build the model. We worked through the pseudocode together, and then she sat with me while I implemented them. I read the textbook, watched the lectures, and reached out to my TA, and still have trouble understanding the goal of this lab.
from asyncio import sleep

from Altered_Maze import Maze
import numpy as np

class Robot:
    def __init__(self, maze, sequence):
        self.maze = maze #given maze for the robot to search through
        self.width = maze.width
        self.height = maze.height
        self.colors = ['r', 'b', 'g', 'y']  # all the possible colors a square could be
        self.sequence = sequence #randomly generated sequence of moves we want the robot to traverse
        self.maze_colors = self.find_square_colors()
        self.color_counts = self.calc_color_counts()[0] #keeps track of how many sqaure colors there are for calculating probabilities later
        self.tile_count = self.calc_color_counts()[1] #keeps track of the total number of coords that are actually legal floor tiles
        self.final_probabilities = {} #final dictionary to be printed that maps time steps to probabilities at that time.
        self.states = self.maze_colors.keys()
        self.transitions = {}
        self.observations = {}


        self.model = self.build_model()
        self.initialize_probabilities()

    def find_square_colors(self): #returns a dictionary of sqaure coordinates mapped to their colors
        coord_to_colors = {}
        for x in range(self.width):
            for y in range(self.height):
                if self.maze.is_floor(x, y):
                    coord_to_colors[(x, y, self.maze.map[maze.index(x,y)])] = self.maze.index(x, y)
        return coord_to_colors


    def initialize_probabilities(self): #returns the dictionary of every sqaure coordinate mapped to its initial probability
        for time in range(0, len(self.sequence)+1): #for every time step
            probabilities = {}  #make a dictionary of probabilities from coordinate to its probability value.
            for x in range(maze.width):
                for y in range(maze.height):
                    if maze.is_floor(x, y): #only add that state if it's a floor and not a wall
                        state = (x, y, maze.map[maze.index(x, y)])
                        probabilities[state] = 1/self.tile_count
            self.final_probabilities[time] = probabilities

    def calc_color_counts(self): #keeps track of how many of each color tile there are
        tile_count = 0
        map = self.maze.map
        color_counts =  {'r': 0, 'g': 0, 'b': 0, 'y': 0}
        for x in range(self.width):
            for y in range(self.height):
                if map[self.maze.index(x, y)] == 'r':
                    color_counts['r'] += 1
                    tile_count += 1
                if map[self.maze.index(x, y)] == 'g':
                    color_counts['g'] += 1
                    tile_count += 1
                if map[self.maze.index(x, y)] == 'b':
                    color_counts['b'] += 1
                    tile_count += 1
                if map[self.maze.index(x, y)] == 'y':
                    color_counts['y'] += 1
                    tile_count += 1
        return (color_counts, tile_count)


    def is_neighbor(self, x1, y1, x2, y2): #helper function to find a neighbor when building the transition model
        if (x1 == x2 and abs(y1 - y2) == 1):
            return True
        if (y1 == y2 and abs(x1 - x2) == 1): #if the x's or y's are the same and the other coord is 1 off, they're next to one another
            return True
        else:
            #print("not a neighbor!")
            return False

    def track_observations(self, observation_dict, color, state):
        for col in self.colors:
            if col == color:
                observation_dict[col] = 0.88 #.88 chance the color is sensed correctly
            else:
                #print('here')
                observation_dict[col] = 0.04 #every other color only has a .4 chance
        self.observations[state] = observation_dict

    def normalize_values(self, state, tiles):
        state = (self.color_counts[state[2]] / tiles)
        return state

    def forward_backward(self):#*got help from a friend on building this. I had, and still do, have trouble visualizing this model clearly, so we worked through it together with pseudocode.
        for time in range(0, len(self.sequence)):
            x = self.sequence[time][0]
            y = self.sequence[time][1]
            color = self.sequence[time][2]
            #print("color at: " + str(x) + ", " + str(y) + " is " + str(color))

            tiles = 0
            for state in self.states:
                total_probability = 0 #should equal 1 by the end of calculations
                for state2 in self.states:
                    prob = (self.final_probabilities[time])[state2]  # original probability of this state. Should be uniform at the start for all states
                    #print("probability: " + str(prob))
                    new_prob = ((self.transitions[state])[state2]) * prob * 10 # probability of transitioning from the last state
                    #print(new_prob)
                    total_probability += new_prob
                total_probability = total_probability * ((self.observations[state])[color])
                self.final_probabilities[time][state] = total_probability
                tiles += total_probability

            for state in self.states:
                self.normalize_values(state, tiles)

    def build_model(self): #builds the model by adding to a global transition and observation dictionaries
        for state1 in self.states:
            transitions = {}  # other states to transition probabilities
            observations = {}  # colors to their probability
            x1 = state1[0] #coords of the first state
            y1 = state1[1]
            color = state1[2]

            self.track_observations(observations, color, state1) #helper function to build the sensor observations

            i = 0  # number of neighbors accounted for
            for state2 in self.states:  # for all possible neighbors of state1
                x2 = state2[0] #coords of second state
                y2 = state2[1]
                if self.is_neighbor(x1, y1, x2, y2):  # if state 2 is a neighbor of state 1
                    transitions[state2] = 1  # transition probability is 1
                    i += 1
                else:  # if state2 isn't a neighbor, then we can't transition to it yet, so it's transition probability is 0
                    transitions[state2] = 0

            for s in self.states:  # normalize using count (always 4 for 4 directions)
                transitions[s] = (transitions[s]) / i
            self.transitions[state1] = transitions  # add to overall transition dictionary

    def animate_path(self, path): #print out the maze of the robot's path. Takes the coordinates from Altered_Maze.py
        # reset the robot locations in the maze
        self.maze.robotloc = path[0]
        i = 0
        for state in path:
            list = []
            x = state[0]
            y = state[1]
            list.append(x)
            list.append(y)
            self.maze.robotloc = tuple(list)
            print("Robot is at position: " + str(i))
            i += 1
            print(str(self.maze))


    def __str__(self):
        string = ""
        times = list(self.final_probabilities.keys())
        times.reverse()

        i = 0
        for time in times:
            string += ("probabilities at time-step " + str(i) + " are: " + str(self.final_probabilities[time]))
            string += "\n"
            string += "\n"
            i += 1
        return string


if __name__ == '__main__':
    maze = Maze('maze1.maz')
    robot = Robot(maze, [(1, 0, 'r'), (1, 1,'g'), (1, 2, 'b'), (1, 3, 'b')])
    #print(robot.calc_color_counts()[1])
    #print(robot.tile_count)
    #print(robot.final_probabilities)
    #print(robot.states)
    #print(robot.transitions.keys())
    #print(robot.observations)
    robot.forward_backward()
    print(robot)
    print(robot.animate_path([(1,0) , (1,1), (1,2), (1,3)]))




