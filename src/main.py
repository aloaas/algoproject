import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import numpy as np
from maze import *
from ants import *

frame = Tk()
frame.title("Program")
frame.geometry("1280x720")

c_width = 1024
c_height = 720
canvas = Canvas(frame, width = c_width, height = c_height)
canvas.configure(background = "white")
canvas.grid(row = 0, column = 0, rowspan = 50, columnspan = 1)

#value based on pixel color
color = ["white", "gray", "green", "blue"]

class MazeCanvas():

    def __init__(self, frame, canvas):
        self.daemon = True
        self.frame = frame
        self.canvas = canvas
        self.color = ["white", "gray", "green", "blue"]
        self.maze = []
        self.x_init = 10
        self.y = 10
        self.cell_width = None
        self.cell_height = None
        self.rectangles = []
        self.ants = []
        self.func = None
        self.in_loop = False

    def run(self):
        if self.in_loop:
            locations, pheromones = next(self.func)
        else:
            self.func = ant_colony(self.maze,
                                                n_ants=5, step_by_step=False,
                                                vaporization_rate=0.98)
            self.in_loop = True
            locations, pheromones = next(self.func)
        for rectangle in self.rectangles:
            self.canvas.delete(rectangle)
        for ant in self.ants:
            self.canvas.delete(ant)
        y_init = self.y

        minval = np.min(pheromones)
        maxval = np.max(pheromones)
        print(locations)
        loc_y = 0
        for row in pheromones:
            x = self.x_init
            loc_x = 0
            for pixel in row:
                if pixel >0:
                    value = int(((pixel - minval)/(maxval - minval))*255)
                    fill = self.from_rgb((255-value, 255-value//2, 255-value//2))
                    cell = self.canvas.create_rectangle(x+0.25*self.cell_width, self.y+0.25*self.cell_height, x+0.75*self.cell_width, self.y+0.75*self.cell_height, fill = fill, outline = fill)
                    self.rectangles.append(cell)
                for ant_y, ant_x in locations:
                    if ant_x == loc_x and ant_y == loc_y:
                        ant = self.canvas.create_oval(x + 0.4 * self.cell_width, self.y + 0.4 * self.cell_height, x + 0.6 * self.cell_width, self.y + 0.6 * self.cell_height, fill="pink", outline="pink")
                        self.ants.append(ant)
                x += self.cell_width
                loc_x+=1
            self.y += self.cell_height
            loc_y += 1
        self.canvas.update()
        self.y = y_init
        loc_y = 0
        self.frame.after(100, self.run)
        #print(locations, pheromones)
        
    #https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
    def from_rgb(self, rgb):
        """translates an rgb tuple of int to a tkinter friendly color code
        """
        return "#%02x%02x%02x" % rgb

    def maze_gen(self):
        self.canvas.delete("all")    #clear whatever was previously on screen
        #try to get input value or reset to default
        maze_width = 50 if len(width_input.get()) == 0 else int(width_input.get())
        maze_height = 50 if len(height_input.get()) == 0 else int(height_input.get())
        f = 5 if len(food_input.get()) == 0 else int(food_input.get())

        ix, iy = 1, 1  # home location

        self.maze = Maze(maze_width//2, maze_height//2, ix, iy, f).make_maze()

        #add padding to maze in canvas
        self.x_init = c_width //(maze_width //2)
        self.y = c_height// (maze_height //2)

        #calculate cell size based on maze size
        self.cell_width = (c_width - 2*self.x_init)//maze_width
        self.cell_height = (c_height-2*self.y)// maze_height

        #adding rectangles
        for row in self.maze:
            x = self.x_init
            for pixel in row:
                fill = self.color[pixel]
                self.canvas.create_rectangle(x, self.y, x+self.cell_width, self.y+self.cell_height, fill = fill, outline = fill)
                x += self.cell_width
            self.y += self.cell_height
        self.x_init = c_width //(maze_width //2)
        self.y = c_height// (maze_height //2)


# failsafe for numeric input
def is_numeric(S):
    if len(set(list(S)) - {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}) == 0:
        return True
    frame.bell() # .bell() plays that ding sound telling you there was invalid input
    return False

#https://stackoverflow.com/questions/41477428/ctrl-a-select-all-in-entry-widget-tkinter-python
# support for CTRL + a
def callback(event):
    frame.after(50, select_all, event.widget)

def select_all(widget):
    # select text
    widget.select_range(0, 'end')
    # move cursor to the end
    widget.icursor('end')


vcmd = (frame.register(is_numeric), '%S')

#set initial values for entries
initial_val_width = StringVar(frame, value='50')
initial_val_height= StringVar(frame, value='50')
initial_val_food = StringVar(frame, value='10')

#user input widgets
width_input= Entry(frame, validate='key', vcmd=vcmd, textvariable = initial_val_width)
width_label = Label(text="Width:")
width_label.grid(row = 0, column = 1,  sticky=W)
width_input.grid(row = 1, column = 1, columnspan = 1, sticky = E+W)
width_input.bind('<Control-a>', callback)

height_input =  Entry(frame,  validate='key', vcmd=vcmd, textvariable = initial_val_height)
height_label = Label(text="Height:")
height_label.grid(row = 2, column = 1, sticky=W)
height_input.grid(row = 3, column = 1,sticky = E+W)
height_input.bind('<Control-a>', callback)

food_input =  Entry(frame,  validate='key', vcmd=vcmd, textvariable = initial_val_food)
food_label = Label(text="Number of food locations:")
food_label.grid(row = 4, column = 1, sticky=W)
food_input.grid(row = 5, column = 1,sticky = E+W)
food_input.bind('<Control-a>', callback)

mazecanvas = MazeCanvas(frame, canvas)
create_maze_button = Button(frame, text="Generate maze", command = mazecanvas.maze_gen)
create_maze_button.grid(row = 6, column = 1, sticky = W+E+N+S)

start_button = Button(frame, text="Start algorithm", command = mazecanvas.run)
start_button.grid(row = 7, column = 1, sticky = W+E+N+S)

frame.mainloop()