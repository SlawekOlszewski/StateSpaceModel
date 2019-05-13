from win32api import GetSystemMetrics
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *
import matplotlib
from math import *
matplotlib.use('TkAgg')


class StateSpace:
    def __init__(self,  window):
        self.window = window
        self.Height = 120
        self.Width = 180
        self.window.geometry("%dx%d+%d+%d" % (self.Width, self.Height, (GetSystemMetrics(0)-self.Width)/2,
                             (GetSystemMetrics(1)-self.Height)/2))
        self.window.resizable(width=False, height=False)
        self.window.title("Model stanowy wyższego rzędu")

        self.N = Entry(window)
        self.labelN = Label(text="N")

        self.A = Entry(window)
        self.labelA = Label(text="A")

        self.B = Entry(window)
        self.labelB = Label(text="B")

        self.T = Entry(window)
        self.labelT = Label(text="T")

        self.labelStability = Label(text="")

        self.button = Button (window, text="Wykreśl", command=self.calculate)

        self.labelN.place(x=0, y=0)
        self.N.place(x=20,y=0)
        self.labelA.place(x=0, y=20)
        self.A.place(x=20, y=20)
        self.labelB.place(x=0, y=40)
        self.B.place(x=20, y=40)
        self.labelT.place(x=0, y=60)
        self.T.place(x=20, y=60)
        self.button.place(x=60, y=80)
        self.labelStability.place(x=15, y=120)

    def stability_test(self, matrix):
        roots = np.real(np.roots(np.poly(matrix)))
        stability = np.zeros(matrix.shape[1])
        for i in range(0,len(roots)):
            if roots[i] < 0:
                stability[i] = True
            else:
                stability[i] = False
        if np.all(stability):
            return True
        else:
            return False

    def calculate (self):
        number = int(self.N.get())
        t = float(self.T.get())
        a = np.identity(number)
        a = np.delete(a, (number - 1), axis=0)
        zero = np.zeros(number)
        a = np.vstack((zero, a))
        b = np.zeros(number)
        local_a = self.A.get()
        local_a = local_a.split()
        for i in range(len(local_a)):
            local_a[i] = int(local_a[i])
        local_b = self.B.get()
        local_b = local_b.split()
        for i in range(len(local_b)):
            local_b[i] = int(local_b[i])
        for i in range(number):
            a[i][number - 1] = -1 * local_a[i]
            b[i] = local_b[i]
        c = np.zeros(number)
        c[number - 1] = 1
        b = np.asmatrix(b)
        b = b.transpose()
        c = np.asmatrix(c)
        ###############
        stabilityReturn = self.stability_test(a)
        if stabilityReturn:
            self.stabilityText = "System stabilny!"
        else:
            self.stabilityText = "System niestabilny!"

        self.labelStability.config(text=self.stabilityText, font=("times", 14), fg="red")
        ################
        h = 0.001
        num = int(t / h)
        ystep = np.zeros(num)
        ysin = np.zeros(num)
        ysquare = np.zeros(num)

        # u = step
        step = np.array(np.ones(num))

        # u = sinus
        sinus = np.zeros(num)
        period = 2 # okres sinusa
        for i in range(0, num):
            sinus[i] = sin(i * h / period * 2 * pi)

        # u = square
        square = np.zeros(num)
        period = 2  # okres prostokata
        for i in range(0, num):
            if int(i*h)%period == 0:
                square[i] = 1
            else:
                square[i] = 0

        # pobudzenie skokiem
        x = np.zeros([number, num])
        for i in range(0, num - 1):
            for j in range(0, number):
                x[j, i + 1] = x[j, i] + h * (a[j, :] @ x[:, i] + b[j, 0] * step[i])
        ystep = c @ x
        ystep = ystep.transpose()

        # pobudzenie sinusem
        x = np.zeros([number, num])
        for i in range(0, num - 1):
            for j in range(0, number):
                x[j, i + 1] = x[j, i] + h * (a[j, :] @ x[:, i] + b[j, 0] * sinus[i])
        ysin = c @ x
        ysin = ysin.transpose()

        # pobudzenie prostokatem
        x = np.zeros([number, num])
        for i in range(0, num - 1):
            for j in range(0, number):
                x[j, i + 1] = x[j, i] + h * (a[j, :] @ x[:, i] + b[j, 0] * square[i])
        ysquare = c @ x
        ysquare = ysquare.transpose()

        i = np.linspace(0, num, num)

        fig = Figure(figsize=(12,4))
        pltStep = fig.add_subplot(131)
        pltSin = fig.add_subplot(132)
        pltSquare = fig.add_subplot(133)

        pltStep.plot(i, ystep, "r-")
        pltStep.plot(i, step, "b-")
        pltStep.grid()
        pltSin.plot(i, ysin, "r-")
        pltSin.plot(i, sinus, "b-")
        pltSin.grid()
        pltSquare.plot(i, ysquare, "r-")
        pltSquare.plot(i, square, "b-")
        pltSquare.grid()

        pltStep.set_title ("Pobudzenie skokiem", fontsize=16)
        pltStep.set_ylabel("y(t)", fontsize=12)
        pltStep.set_xlabel("t", fontsize=12)
        pltStep.set_xticks(np.arange(0, num + 1, int(1 / h)))
        pltStep.set_xticklabels(np.arange(0, int(t + 1), 1))

        pltSin.set_title("Pobudzenie sinusem", fontsize=16)
        pltSin.set_ylabel("y(t)", fontsize=12)
        pltSin.set_xlabel("t", fontsize=12)
        pltSin.set_xticks(np.arange(0, (num + 1), int(1/h)))
        pltSin.set_xticklabels(np.arange(0, int(t + 1), 1))

        pltSquare.set_title("Pobudzenie prostokątem", fontsize=16)
        pltSquare.set_ylabel("y(t)", fontsize=12)
        pltSquare.set_xlabel("t", fontsize=12)
        pltSquare.set_xticks(np.arange(0, num + 1, int(1 / h)))
        pltSquare.set_xticklabels(np.arange(0, int(t + 1), 1))

        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().place(x=170, y=10)
        canvas.draw()
        self.Height = 420
        self.Width =  GetSystemMetrics(0) - 100
        self.window.geometry("%dx%d+%d+%d" % (self.Width, self.Height, 50,
                                              (GetSystemMetrics(1) - self.Height) / 2))


def main():
    tkClass = Tk()
    StateSpace(tkClass)
    tkClass.mainloop()


if __name__ == "__main__":
    main()
