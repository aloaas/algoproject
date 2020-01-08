from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import numpy as np
from maze import *

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


def maze_gen():
    canvas.delete("all")    #clear whatever was previously on screen
    #try to get input value or reset to default
    maze_width = 50 if len(width_input.get()) == 0 else int(width_input.get())
    maze_height = 50 if len(height_input.get()) == 0 else int(height_input.get())
    f = 5 if len(food_input.get()) == 0 else int(food_input.get())

    ix, iy = 1, 1  # home location

    maze = Maze(maze_width//2, maze_height//2, ix, iy, f).make_maze()

    #add padding to maze in canvas
    x_init = c_width //(maze_width //2)
    y = c_height// (maze_height //2)

    #calculate cell size based on maze size
    cell_width = (c_width - 2*x_init)//maze_width
    cell_height = (c_height-2*y)// maze_height

    #adding rectangles
    for row in maze:
        x = x_init
        for pixel in row:
            fill = color[pixel]
            canvas.create_rectangle(x, y, x+cell_width, y+cell_height, fill = fill, outline = fill)
            x += cell_width
        y += cell_height


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


create_maze_button = Button(frame, text="Generate maze", command = maze_gen)
create_maze_button.grid(row = 6, column = 1, sticky = W+E+N+S)


frame.mainloop()