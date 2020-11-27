import random
import tkinter as tk
import tkinter.font as tk_font
from tkinter import messagebox
import math

BORDER_WIDTH = 3
TINY = 3e-10


def polynomial_least_squares(points, degree):
    if degree >= len(points):
        raise Exception('The number of points should be greater than the degree')

    # allocate space for (degree + 1) equations with
    # (degree + 1) unknowns
    coeffs = [[0] * (degree + 1) for _ in range(degree + 1)]

    # calculate in the coefficients
    for k in range(degree + 1):
        # fill in coefficients for the partial and
        # then derivative with respect to Ak

        for a_sub in range(degree + 1):
            # calculate in the A < a_sub > term

            coeffs[k][a_sub] = 0
            for i in range(len(points)):
                coeffs[k][a_sub] += math.pow(points[i][0], k + a_sub)

    # calculate the constant values
    values = [0] * (degree + 1)
    for k in range(degree + 1):
        values[k] = 0
        for i in range(len(points)):
            values[k] += points[i][1] * math.pow(points[i][0], k)

    # solve the equations
    return gaussian_eliminate(coeffs, values)


def gaussian_eliminate(coeffs, values):
    # number of rows and columns before augmenting the matrix
    row = len(coeffs)
    col = len(coeffs[0])

    # augmenting the matrix
    aug = []
    for r in range(row):
        aug.append([])
        for val in coeffs[r]:
            aug[r].append(val)
        aug[r].append(float(values[r]))

    for r in range(row - 1):
        # zero out all the entries in this column after this row
        # see if this row has a non-zero entry
        if abs(aug[r][r]) < TINY:
            # the value is too close to zero, try to swab it with a later row
            for r2 in range(r + 1, row):
                if abs(aug[r2][r]) > TINY:
                    # this will work, swab them
                    for c in range(col + 1):
                        aug[r][c], aug[r2][c] = aug[r2][c], aug[r][c]
                    break

        # if aug[r][r] is still zero
        if abs(aug[r][r]) < TINY:
            # no later row has a non-zero entry in this column
            raise ValueError("There is no unique solution")

        # zero out the entries in column r after this row
        for r2 in range(r + 1, row):
            factor = -aug[r2][r] / aug[r][r]
            for c in range(r, col + 1):
                aug[r2][c] += factor * aug[r][c]

    # check if we have a solution
    if abs(aug[row - 1][col - 1]) < TINY:
        # there is no solution
        # see if all the entries in this row are zero
        all_zeros = True
        for c in range(col + 1):
            if abs(aug[row - 1][c]) > TINY:
                all_zeros = False
                break

        if all_zeros:
            raise ValueError('The solution is not unique')
        else:
            raise ValueError('There is no solution')

    # back substitute
    sol = [0 for i in range(row)]
    for r in range(row - 1, -1, -1):
        sol[r] = aug[r][col]
        for r2 in range(r + 1, row):
            sol[r] -= sol[r2] * aug[r][r2]
        sol[r] /= aug[r][r]

    return sol


def func(a_values, x):
    result = 0
    factor = 1
    for i in range(len(a_values)):
        result += a_values[i] * factor
        factor *= x
    return result


class App:
    ''' The tkinter GUI interface '''

    def kill_callback(self):
        self.window.destroy()

    def __init__(self):
        # start with no data points
        self.points = []
        self.solved = False

        # set up tkinter
        self.window = tk.Tk()
        self.window.title('Polynomial Least Squares')
        self.window.protocol('WM_DELETE_WINDOW', self.kill_callback)
        self.window.geometry('300x378')

        # canvas
        self.canvas = tk.Canvas(self.window, width=50, height=50, relief=tk.RIDGE, bd=BORDER_WIDTH,
                                highlightthickness=0, bg='white')
        self.canvas.pack(padx=5, pady=5, side=tk.TOP, fill=tk.BOTH, expand=1)

        # parameters
        parameter_frame = tk.Frame(self.window)
        parameter_frame.pack(padx=5, pady=5, side=tk.BOTTOM)

        degree_label = tk.Label(parameter_frame, text='Degree:')
        degree_label.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.degree_entry = tk.Entry(parameter_frame, width=4, justify=tk.RIGHT)
        self.degree_entry.grid(row=0, column=1, padx=5, pady=2)
        self.degree_entry.insert(tk.END, '3')

        solve_button = tk.Button(parameter_frame, text='Solve', width=10, command=self.solve)
        solve_button.grid(row=0, column=2, padx=5, pady=2)
        reset_button = tk.Button(parameter_frame, text='Reset', width=10, command=self.reset)
        reset_button.grid(row=0, column=3, padx=5, pady=2)

        a_values_label = tk.Label(parameter_frame, text="A's:")
        a_values_label.grid(row=1, column=0, padx=5, pady=2, sticky=tk.W + tk.N)
        self.a_values_list = tk.Listbox(parameter_frame, height=5)
        self.a_values_list.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky=tk.W + tk.E)

        # bind some keys
        self.window.bind('<Return>', (lambda e, button=solve_button: solve_button.invoke()))

        # catch mouse clicks
        self.canvas.bind('<Button-1>', self.mouse_click)

        # Force focus so Alt+F4 closes this window and not the Python shell.
        self.window.focus_force()
        self.window.mainloop()

    def mouse_click(self, event):
        self.points.append((event.x, event.y))
        self.solved = False
        self.draw()

    def reset(self):
        self.points = []
        self.solved = False
        self.draw()

    def solve(self):
        ''' Perform polynomial least squares '''
        try:
            self.a_values_list.delete(0, tk.END)
            self.solved = False

            degree = int(self.degree_entry.get())
            self.a_values = polynomial_least_squares(self.points, degree)

            # display the A's
            for k in range(len(self.a_values)):
                self.a_values_list.insert(tk.END, f'A[{k}] = {self.a_values[k]}')
            self.solved = True
        except Exception as e:
            messagebox.showinfo('Error', str(e))

        self.draw()

    def draw(self):
        ''' Draw the points and least squares fit '''
        self.canvas.delete(tk.ALL)

        # draw the points
        radius = 2
        for point in self.points:
            x0 = point[0] - radius
            y0 = point[1] - radius
            x1 = point[0] + radius
            y1 = point[1] + radius
            self.canvas.create_oval(x0, y0, x1, y1, fill='red', outline='red')

        # if we have a solution
        if self.solved:
            curve = []
            for x in range(self.canvas.winfo_width()):
                curve.append((x, func(self.a_values, x)))
            self.canvas.create_line(curve, fill='blue')
            self.verticals()

    def verticals(self):
        for point in self.points:
            x = point[0]
            y0 = point[1]
            y1 = func(self.a_values, x)
            self.canvas.create_line(x, y0, x, y1, fill='green')


if __name__ == '__main__':
    app = App()
