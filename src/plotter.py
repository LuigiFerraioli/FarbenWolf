"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class FlaechenPlotter:
    """
    A 3D surface plotter for visualizing room wall and ceiling configurations.

    This class allows you to define the dimensions of a room (length, width, 
    and two heights for handling slopes) and visualize different wall/ceiling 
    configurations in 3D using matplotlib.

    Attributes:
        l (float): Length of the area.
        b (float): Width of the area.
        h1 (float): First height value (possibly lower/slope side).
        h2 (float): Second height value.
        select_type (str): Selected type of surface to plot.
        plt (module): Reference to matplotlib.pyplot.
        _fig (matplotlib.figure.Figure or None): Reference to the active figure, if any.

    Methods:
        close_figure(): Closes any existing figure.
        set_parameters(l, b, h1, h2, select_type): Updates plot parameters.
        draw_shape(verts, title): Draws a 3D shape using provided vertices.
        normalize_dimensions(): Ensures all dimensions are valid and consistent.
        plot(): Generates and shows the selected wall/ceiling layout.
    """

    def __init__(self, l=2, b=3, h1=2, h2=3, select_type="Alle Wände mit Decke"):
        """
        Initialize the FlaechenPlotter with given dimensions and plot type.

        Args:
            l (float): Length of the area. Defaults to 2.
            b (float): Width of the area. Defaults to 3.
            h1 (float): First height value (can be lower or sloped). Defaults to 2.
            h2 (float): Second height value. Defaults to 3.
            select_type (str): Type of surface/wall configuration. Defaults to "All walls with ceiling".
        """
        self.l = l if l != 0 else 1
        self.b = b if b != 0 else 1
        self.h1 = h1 if h1 != 0 else 1
        self.h2 = h2 if h2 != 0 else 2
        if self.h2 != 0 and self.h1 > self.h2:
            self.h1, self.h2 = self.h2, self.h1
        self.select_type = select_type
        self.plt = plt
        self._fig = None

    def close_figure(self):
        """
        Close the current matplotlib figure if it exists.
        """
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None

    def set_parameters(self, l, b, h1, h2, select_type):
        """
        Set new parameters for the plotter.

        Args:
            l (float): New length.
            b (float): New width.
            h1 (float): New first height.
            h2 (float): New second height.
            select_type (str): New wall configuration type.
        """
        self.l = l
        self.b = b
        self.h1 = h1
        self.h2 = h2
        if self.h2 != 0 and self.h1 > self.h2:
            self.h1, self.h2 = self.h2, self.h1
        self.select_type = select_type

    def draw_shape(self, verts, title):
        """
        Draws a 3D shape using the given vertices and displays it in a matplotlib window.

        Parameters:
            verts (list of list of tuples): A list of polygons, where each polygon is defined 
                by a list of (x, y, z) vertices. Used to construct the 3D shape.
            title (str): The title for the plot window and the 3D figure.

        Behavior:
            - Closes any previously opened figure.
            - Creates a new 3D figure and adds the shape using Poly3DCollection.
            - Sets axis limits based on the object's dimensions (self.l, self.b, self.h1, self.h2).
            - Displays the plot non-blocking.

        Note:
            Axis labels are set in German:
                - 'Länge' (Length) for x-axis
                - 'Breite' (Width) for y-axis
                - 'Höhe' (Height) for z-axis
        """
        if self._fig is not None:
            plt.close(self._fig)

        self._fig = plt.figure(figsize=(6, 6))
        ax = self._fig.add_subplot(111, projection='3d')
        ax.add_collection3d(Poly3DCollection(
            verts, facecolors='skyblue', edgecolors='k', linewidths=1, alpha=0.9))
        self._fig.canvas.manager.set_window_title(title)

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.zaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(title)
        ax.set_xlim(-1, abs(self.l) + 1)
        ax.set_ylim(-1, abs(self.b) + 1)
        ax.set_zlim(0, max(self.h1, self.h2) + 1)
        ax.set_xlabel('Länge')
        ax.set_ylabel('Breite')
        ax.set_zlabel('Höhe')
        plt.show(block=False)

    def normalize_dimensions(self):
        """
        Ensure that all dimensions are valid and adjust if necessary.
        Sets any zero dimensions to 1 and ensures h1 is not greater than h2.
        """
        self.l = self.l if self.l != 0 else 1
        self.b = self.b if self.b != 0 else 1
        self.h1 = self.h1 if self.h1 != 0 else 1
        self.h2 = self.h2

        if self.h2 != 0 and self.h1 > self.h2:
            self.h1, self.h2 = self.h2, self.h1

    def plot(self):
        """
        Generate and display the selected wall/ceiling configuration.
        Must be implemented according to the 'select_type'.
        """
        self.normalize_dimensions()
        t = self.select_type
        if t == "Decke/Bodenfläche":
            verts = [[[0, 0, 0], [self.l, 0, 0], [
                self.l, self.b, 0], [0, self.b, 0]]]

        elif t == "Wand (rechteckig)":
            verts = [[[0, 0, 0], [self.l, 0, 0], [
                self.l, 0, self.h1], [0, 0, self.h1]]]

        elif t == "Wand (dreieckig)":
            verts = [[[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h1]]]

        elif t == "Zwei gegenüberliegende Wände":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h1], [0, 0, self.h1]],
                [[0, self.b, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [0, self.b, self.h1]]
            ]

        elif t == "Zwei nebeneinanderliegende Wände":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h1], [0, 0, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]]
            ]

        elif t == "Alle Wände ohne Decke/Sockel":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h1], [0, 0, self.h1]],
                [[0, self.b, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [0, self.b, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]],
                [[self.l, 0, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [self.l, 0, self.h1]]
            ]

        elif t == "Alle Wände mit Decke":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h1], [0, 0, self.h1]],
                [[0, self.b, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [0, self.b, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]],
                [[self.l, 0, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [self.l, 0, self.h1]],
                [[0, 0, self.h1], [self.l, 0, self.h1], [
                    self.l, self.b, self.h1], [0, self.b, self.h1]]
            ]

        elif t == "Alle Wände mit einer schrägen Wand (ohne Decke)":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h2], [0, 0, self.h1]],
                [[0, self.b, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h2], [0, self.b, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]],
                [[self.l, 0, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h2], [self.l, 0, self.h2]]
            ]

        elif t == "Alle Wände mit einer schrägen Wand und Decke":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h2], [0, 0, self.h1]],
                [[0, self.b, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h2], [0, self.b, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]],
                [[self.l, 0, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h2], [self.l, 0, self.h2]],
                [[0, 0, self.h1], [0, self.b, self.h1], [
                    self.l, self.b, self.h2], [self.l, 0, self.h2]]
            ]

        elif t == "Fassade (Flachdach)":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h1],
                    [0, 0, self.h1]], [[0, self.b, 0], [self.l, self.b, 0],
                                       [self.l, self.b, self.h1], [0, self.b, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]],
                [[self.l, 0, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [self.l, 0, self.h1]]
            ]

        elif t == "Fassade (Satteldach)":
            verts = [
                [[0, 0, 0], [self.l/2, 0, 0], [self.l/2, 0, self.h2], [0, 0, self.h1]],
                [[self.l/2, self.b, 0], [self.l/2, self.b, self.h2],
                    [self.l, self.b, self.h1], [self.l, self.b, 0]],
                [[0, self.b, 0], [self.l/2, self.b, 0],
                    [self.l/2, self.b, self.h2], [0, self.b, self.h1]],
                [[self.l/2, 0, 0], [self.l/2, 0, self.h2],
                    [self.l, 0, self.h1], [self.l, 0, 0]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]],
                [[self.l, 0, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h1], [self.l, 0, self.h1]]
            ]

        elif t == "Fassade (Doppelhaushälfte)":
            verts = [
                [[0, 0, 0], [self.l, 0, 0], [self.l, 0, self.h2], [0, 0, self.h1]],
                [[0, self.b, 0], [self.l, self.b, 0], [
                    self.l, self.b, self.h2], [0, self.b, self.h1]],
                [[0, 0, 0], [0, self.b, 0], [0, self.b, self.h1], [0, 0, self.h1]]
            ]

        else:
            print("Unbekannter Typ:", t)
            return

        self.draw_shape(verts, t)
