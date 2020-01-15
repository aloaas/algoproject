from tkinter import *

from maze import *
from ants import *
from PIL import Image, ImageTk

frame = Tk()
frame.title("Program")
frame.geometry("1600x900")
bgcolor = "white"
frame.configure(background=bgcolor)
frame.resizable(False, False)

c_width = 1280
c_height = 900
canvas = Canvas(frame, width=c_width, height=c_height)
canvas.configure(background="white")
canvas.grid(row=0, column=0, rowspan=50, columnspan=1)



# value based on pixel color
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
        self.foods = []
        self.func = None
        self.in_loop = False
        self.prev_locations = None
        self.iterations = 1

    def run(self):
        if self.in_loop:
            locations, pheromones, score, food_values = next(self.func)
            score_var.set("Score: " + str(round(score, 5)))
            score_over_time_var.set("Score over time: " + str(round(score / self.iterations, 5)))
        else:
            no_ants = 5 if len(ants_input.get()) == 0 else int(ants_input.get())

            self.func = ant_colony(self.maze,
                                   n_ants=no_ants, step_by_step=False,
                                   vaporization_rate=vp_rate_var.get(),
                                   Q=q_var.get(),
                                   pheromone_weight=pheromone_weight_var.get(),
                                   food_taken = food_taken_var.get(),
                                   food_restore_rate=food_restore_rate_var.get())

            locations, pheromones, score, food_values = next(self.func)
            score_var.set("Score: " + str(round(score, 5)))
            score_over_time_var.set("Score over time: " + str(round(score / self.iterations, 5)))


        y_init = self.y
        minval = np.min(pheromones)
        maxval = np.max(pheromones)
        loc_y = 0
        cell_nr = 0
        for food in self.foods:
            canvas.delete(food)
        for row in pheromones:
            x = self.x_init
            loc_x = 0
            for pixel in row:
                if pixel > 0:
                    value = int(((pixel - minval) / (maxval - minval)) * 255)
                    fill = self.from_rgb((255 - value // 2, 255 - value // 2, 255 - value))
                    if not self.in_loop:
                        cell = self.canvas.create_rectangle(x + 0.25 * self.cell_width, self.y + 0.25 * self.cell_height,
                                                            x + 0.75 * self.cell_width, self.y + 0.75 * self.cell_height,
                                                            fill=fill, outline=fill)
                        self.rectangles.append(cell)
                    else:
                        cell = self.rectangles[cell_nr]
                        self.canvas.itemconfig(cell, fill=fill, outline = fill)
                        cell_nr+=1

                x += self.cell_width
                loc_x += 1
            self.y += self.cell_height
            loc_y += 1
        if self.in_loop:
            self.move_ants(locations)
        else:
            for ant_y, ant_x in locations:
                ant = self.canvas.create_image(self.x_init + self.cell_width * ant_x,
                                               y_init + self.cell_height * ant_y, image=self.ant_image_u,
                                               anchor=NW)
                self.ants.append(ant)
        for food_coord, food_val in food_values.items():
            food_y, food_x = food_coord
            food_max = max(food_values.values())
            food_min = min(food_values.values())
            upper = food_val - food_min
            lower = food_max - food_min
            if lower == 0: food_fill = "green"
            else:
                food_value = int((upper / lower) * 255)
                food_fill = self.from_rgb((110 - ((255 - food_value) //5), 255 - (255 - food_value)  // 2, 110 - ((255 - food_value) //5)))
            food_cell = self.canvas.create_rectangle(self.x_init +self.cell_width* food_x,
                                                     y_init +self.cell_height*food_y,
                                                     self.x_init + self.cell_width * (food_x+1),
                                                     y_init + self.cell_height*(food_y + 1),
                                                     fill=food_fill,
                                                     outline = food_fill)
            self.foods.append(food_cell)
        self.canvas.update()
        self.y = y_init
        loc_y = 0
        self.prev_locations = locations
        self.in_loop = True
        self.iterations+= 1
        self.frame.after(30, self.run)


        # print(locations, pheromones)

    # https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter
    def from_rgb(self, rgb):
        """translates an rgb tuple of int to a tkinter friendly color code
        """
        return "#%02x%02x%02x" % rgb
    def move_ants(self, locations):
        for ant, old, new in zip(self.ants, self.prev_locations, locations):
            y_old, x_old = old
            y_new, x_new = new
            x_change = x_new -x_old
            y_change = y_new - y_old
            self.canvas.move(ant, x_change*self.cell_width, y_change*self.cell_height)
            if x_change == 1:
                self.canvas.itemconfig(ant, image = self.ant_image_r)
            if x_change == -1:
                self.canvas.itemconfig(ant, image = self.ant_image_l)
            if y_change == 1:
                self.canvas.itemconfig(ant, image = self.ant_image_d)
            if y_change == -1:
                self.canvas.itemconfig(ant, image = self.ant_image_u)
            canvas.tag_raise(ant)
    def maze_gen(self):
        self.canvas.delete("all")  # clear whatever was previously on screen
        # try to get input value or reset to default
        maze_width = 20 if len(width_input.get()) == 0 else int(width_input.get())
        maze_height = 20 if len(height_input.get()) == 0 else int(height_input.get())
        f = 5 if len(food_input.get()) == 0 else int(food_input.get())

        ix, iy = maze_height // 4, maze_width // 4  # home location

        self.maze = Maze(maze_width // 2, maze_height // 2, ix, iy, f).make_maze()

        # add padding to maze in canvas
        self.x_init = c_width // (maze_width // 2)
        self.y = c_height // (maze_height // 2)

        # calculate cell size based on maze size
        self.cell_width = (c_width - 2 * self.x_init) // maze_width
        self.cell_height = (c_height - 2 * self.y) // maze_height

        # adding rectangles
        for row in self.maze:
            x = self.x_init
            for pixel in row:
                fill = self.color[pixel]
                self.canvas.create_rectangle(x, self.y, x + self.cell_width, self.y + self.cell_height, fill=fill,
                                             outline=fill)
                x += self.cell_width
            self.y += self.cell_height
        self.x_init = c_width // (maze_width // 2)
        self.y = c_height // (maze_height // 2)
        self.ant_image_u = ImageTk.PhotoImage(Image.open("../img/ant_u.png").resize((self.cell_width, self.cell_height)))
        self.ant_image_l = ImageTk.PhotoImage(Image.open("../img/ant_l.png").resize((self.cell_width, self.cell_height)))
        self.ant_image_r = ImageTk.PhotoImage(Image.open("../img/ant_r.png").resize((self.cell_width, self.cell_height)))
        self.ant_image_d = ImageTk.PhotoImage(Image.open("../img/ant_d.png").resize((self.cell_width, self.cell_height)))



# failsafe for numeric input
def is_numeric(S):
    if len(set(list(S)) - {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}) == 0:
        return True
    frame.bell()  # .bell() plays that ding sound telling you there was invalid input
    return False


# https://stackoverflow.com/questions/41477428/ctrl-a-select-all-in-entry-widget-tkinter-python
# support for CTRL + a
def callback(event):
    frame.after(50, select_all, event.widget)


def select_all(widget):
    # select text
    widget.select_range(0, 'end')
    # move cursor to the end
    widget.icursor('end')

frame.grid_columnconfigure(0, weight=1)

vcmd = (frame.register(is_numeric), '%S')

# set initial values for entries
initial_val_width = StringVar(frame, value='20')
initial_val_height = StringVar(frame, value='20')
initial_val_food = StringVar(frame, value='5')
initial_val_ants = StringVar(frame, value='5')

# user input widgets
width_input = Entry(frame, validate='key', vcmd=vcmd, textvariable=initial_val_width, font='Helvetica 12')
width_label = Label(text="Width:", background = bgcolor, font='Helvetica 14 bold')
width_label.grid(row=0, column=1, sticky=W)
width_input.grid(row=0, column=2, sticky=W + E)
width_input.bind('<Control-a>', callback)

height_input = Entry(frame, validate='key', vcmd=vcmd, textvariable=initial_val_height, font='Helvetica 12')
height_label = Label(text="Height:", background = bgcolor, font='Helvetica 14 bold')
height_label.grid(row=1, column=1, sticky=W)
height_input.grid(row=1, column=2, sticky=W + E)
height_input.bind('<Control-a>', callback)

food_input = Entry(frame, validate='key', vcmd=vcmd, textvariable=initial_val_food, font='Helvetica 12')
food_label = Label(text="No. of food:", background = bgcolor, font='Helvetica 14 bold')
food_label.grid(row=2, column=1, sticky=W)
food_input.grid(row=2, column=2, sticky=W + E)
food_input.bind('<Control-a>', callback)

ants_input = Entry(frame, validate='key', vcmd=vcmd, textvariable=initial_val_ants, font='Helvetica 12')
ants_label = Label(text="No. of ants:", background = bgcolor, font='Helvetica 14 bold')
ants_label.grid(row=3, column=1, sticky=W)
ants_input.grid(row=3, column=2, sticky=W + E)
ants_input.bind('<Control-a>', callback)

q_var = DoubleVar()
q_label = Label(text="Q: ", background = bgcolor, font='Helvetica 12 bold')
q_scale = Scale(frame, from_=1, to=100, resolution = 1, orient = HORIZONTAL, variable = q_var, background = bgcolor, font = "Helvetica 12")
q_scale.set(50)
q_label.grid(row=4, column=1, sticky=W)
q_scale.grid(row=4, column=2, sticky=W + E)

vp_rate_var = DoubleVar()
vp_rate_label = Label(text="Vapor. rate: ", background = bgcolor, font='Helvetica 12 bold')
vp_rate_scale = Scale(frame, from_=0.9, to=1.0, resolution = 0.001, orient = HORIZONTAL, variable = vp_rate_var, background = bgcolor, font = "Helvetica 12")
vp_rate_scale.set(0.999)
vp_rate_label.grid(row=5, column=1, sticky=W)
vp_rate_scale.grid(row=5, column=2, sticky=W + E)

pheromone_weight_var = DoubleVar()
pheromone_weight_label = Label(text="Pheromone w.: ", background = bgcolor, font='Helvetica 12 bold')
pheromone_weight_scale = Scale(frame, from_=0.01, to=1.0, resolution = 0.001, orient = HORIZONTAL, variable = pheromone_weight_var, background = bgcolor, font = "Helvetica 12")
pheromone_weight_scale.set(0.8)
pheromone_weight_label.grid(row=6, column=1, sticky=W)
pheromone_weight_scale.grid(row=6, column=2, sticky=W + E)

food_restore_rate_var = DoubleVar()
food_restore_rate_label = Label(text="Food restore rate: ", background = bgcolor, font='Helvetica 12 bold')
food_restore_rate_scale = Scale(frame, from_=0.001, to=0.5, resolution = 0.001, orient = HORIZONTAL, variable = food_restore_rate_var, background = bgcolor, font = "Helvetica 12")
food_restore_rate_scale.set(0.001)
food_restore_rate_label.grid(row=7, column=1, sticky=W)
food_restore_rate_scale.grid(row=7, column=2, sticky=W + E)


food_taken_var = DoubleVar()
food_taken_label = Label(text="Food taken: ", background = bgcolor, font='Helvetica 12 bold')
food_taken_scale = Scale(frame, from_=0.05, to=1.0, resolution = 0.05, orient = HORIZONTAL, variable = pheromone_weight_var, background = bgcolor, font = "Helvetica 12")
food_taken_scale.set(0.1)
food_taken_label.grid(row=8, column=1, sticky=W)
food_taken_scale.grid(row=8, column=2, sticky=W + E)


mazecanvas = MazeCanvas(frame, canvas)
create_maze_button = Button(frame, text="Generate maze", command=mazecanvas.maze_gen, font='Helvetica 12', background = "azure")
create_maze_button.grid(row=9, column=1,columnspan = 2,  sticky=W + E + N + S, padx = 5, pady = 5)

start_button = Button(frame, text="Start algorithm", command=mazecanvas.run, font='Helvetica 12', background = "azure")
start_button.grid(row=10, column=1,columnspan = 2, sticky=W + E + N + S, padx = 5, pady = 5)

score_var = StringVar()
score_var.set("Total score: ")
score_label = Label(frame, textvariable = score_var, font='Helvetica 12 bold', background = "azure")
score_label.grid(row=11, column=1, columnspan = 2, sticky=W + E + N + S, padx = 5, pady = 5)
score_over_time_var = StringVar()
score_over_time_var.set("Score over time: ")
score_over_time_label = Label(frame, textvariable = score_over_time_var, font='Helvetica 12 bold', background = "azure")
score_over_time_label.grid(row=12, column=1, columnspan = 2, sticky=W + E + N + S, padx = 5, pady = 5)

frame.mainloop()
