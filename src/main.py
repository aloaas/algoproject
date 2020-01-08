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


def maze_gen():
    maze_width = 50 if len(width_input.get()) == 0 else int(width_input.get())
    maze_height = 50 if len(height_input.get()) == 0 else int(height_input.get())

    ix, iy = 1, 1  # home location
    f = 5  # number of food places
    maze = Maze(maze_width, maze_height, ix, iy, f).make_maze()
    x_init = 10
    y = 10
    cell_width = (c_width - 2*x_init)//maze_width
    cell_height = (c_height-2*y)// maze_height

    for row in maze:
        x = x_init
        for pixel in row:
            fill = "black" if pixel == 1 else "white"
            canvas.create_rectangle(x, y, x+cell_width, y+cell_height, fill = fill, outline="black")
            x += cell_width
        y += cell_height


def is_numeric(S):
    if S in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        return True
    frame.bell() # .bell() plays that ding sound telling you there was invalid input
    return False

vcmd = (frame.register(is_numeric), '%S')
width_input= Entry(frame, validate='key', vcmd=vcmd)
height_input =  Entry(frame,  validate='key', vcmd=vcmd)
width_label = Label(text="Width:")
height_label = Label(text="Height:")
width_label.grid(row = 0, column = 1,  sticky=W)
width_input.grid(row = 1, column = 1, columnspan = 1, sticky = E+W)
height_label.grid(row = 2, column = 1, sticky=W)
height_input.grid(row = 3, column = 1,sticky = E+W)

create_maze_button = Button(frame, text="Generate maze", command = maze_gen)
create_maze_button.grid(row = 4, column = 1, sticky = W+E+N+S)


frame.mainloop()