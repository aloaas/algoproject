# Look right and down, if possible add to dictionary
import numpy as np
from collections import defaultdict
from time import sleep

def get_reachable_map(maze):
    reachable=defaultdict(list)
    
    for rownum in range(maze.shape[0]):
        for colnum in range(maze.shape[1]):
            current=(rownum, colnum)
            right=(rownum, colnum+1)
            down=(rownum+1, colnum)
            if maze[current]!=1:
                
                if rownum<maze.shape[0]-1 and maze[down]!=1:
                    reachable[current].append(down)
                    reachable[down].append(current)

                if colnum<maze.shape[1]-1 and maze[right]!=1:
                    reachable[current].append(right)
                    reachable[right].append(current)
            
    return reachable

# Class, , 
# variables: path, current, value of food, maze, reachable_map, pheromone_trail, pheromone_map,   
 #pheromone_weight, Q   
# Functions: select_next, step(leave pheromone, pop from path)
class Ant:
    def __init__(self, maze, reachable_map, pheromone_map, pheromone_weight, Q):
        self.maze = maze #final
        self.reachable_map = reachable_map #final
        self.pheromone_map = pheromone_map # changed when stepping towards home
        self.pheromone_weight = pheromone_weight
        self.Q = Q
        
        
        self.home = tuple(i[0] for i in np.where(maze==3))
        
        # Value of current food, becomes 0 at home
        self.food_value = 0
        # Adds index of base to path
        self.path=[self.home]
        # Set of visited nodes to not visit one node multiple times if possible
        self.visited={self.home}
        
        # How much pheromone the ant leaves with every step
        self.pheromone_trail=0 
        
        self.current=self.home
    
    def step(self):
        # If ant has food, go back
        if self.food_value:
            self.path.pop()
        else:
            chosen=self.select_next()
            # If ant has reached dead end, step backwards
            # TODO leave negative pheromone???
            if chosen==(-1, -1):
                self.path.pop()
            else:
                self.path.append(chosen)
        
        
        self.current=self.path[-1]
        # If food is reached
        if self.maze[self.path[-1]]==2:
            self.food_value=1 # TODO change this to get it from map/food value stuff
            self.pheromone_trail=self.food_value*self.Q/len(self.path)
            
        # If home is reached take food from ant, empty path incase food was not found
        if self.current==self.home:
            self.pheromone_map[self.current]+=self.pheromone_trail
            self.food_value=0
            self.pheromone_trail=0
            self.path=[self.home]
            self.visited={self.home}
                
            
        # Update pheromone map
        self.visited.add(self.current)
        self.pheromone_map[self.current]+=self.pheromone_trail
    
    
    # Returns next selected node or (-1, -1) if ant has reached dead end and has to go backwards.
    def select_next(self):
        # If possible to pick point that has not been picked, pick that
        possibilities = self.reachable_map[self.path[-1]]
        
        not_picked = [i for i in possibilities if i not in self.visited]
        # If only 1 option
        if len(not_picked)==1:
            return not_picked[0]
        
        if len(not_picked)==0:
            return (-1, -1)
        
        probs=np.array([(1-self.pheromone_weight)/len(not_picked)]*len(not_picked))
        pheromone_probs=np.array([self.pheromone_map[i] for i in not_picked])
        pheromone_probs=self.pheromone_weight*(pheromone_probs/pheromone_probs.sum())
                
        probs=probs+pheromone_probs
        chosen=not_picked[np.random.choice(len(not_picked), p=probs)]
        return chosen
    
    
def ant_colony(maze, n_ants=10, vaporization_rate=0.97, pheromone_weight=0.8, 
               n_iterations=1000,  Q=50, step_by_step=False):
    
    pheromones=np.ones(maze.shape)
    pheromones[np.where(maze==1)]=0
    
    reachable_map=get_reachable_map(maze)
    
    ants=[Ant(maze, reachable_map, pheromones, pheromone_weight, Q) for i in range(n_ants)]
    
    for n_iter in range(n_iterations):
        
        locations=[]
        for ant in ants:
            ant.step()
            locations.append(ant.current)
        
        
        pheromones*=vaporization_rate
        # Update maze/Food values
        
        yield locations, pheromones
        if step_by_step:
            input()    
            


