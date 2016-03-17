from random import randint


class Cell(object):

    def __init__(self):
        self.value = 0
        self.clicked = False

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_clicked(self):
        self.clicked = True

    def is_clicked(self):
        return self.clicked


class Grid(object):
    size = 0
    content = []
    llama = -1
    mine = -2
    nb_llamas = 0
    nb_mines = 0

    def __init__(self, size, nb_llamas, nb_mines):
        """Constructor: creates a grid of of size "size" containing 0 on each cell"""

        self.size = size
        self.nb_llamas = nb_llamas
        self.nb_mines = nb_mines

        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(Cell())
            self.content.append(row)

        self.place_item(self.llama, nb_llamas, True)
        self.place_item(self.mine, nb_mines, False)

    def place_item(self, item, amount, is_llama):
        """Generates random coordinates to place llamas or mines on the grid"""
        placed = 0

        while placed < amount:
            row = randint(0, self.size-1)
            col = randint(0, self.size-1)

            if self.content[row][col].value != self.llama and self.content[row][col].value != self.mine:
                self.content[row][col].value = item
                self.set_other_cells(row, col, is_llama)
                placed += 1

    def set_other_cells(self, row, col, is_llama):
        """Counts the number of llamas or mines placed around each cell"""
        counter = 1
        if is_llama:
            counter = 10

        # go to each cell surrounding the current cell
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                # check that the index is within the size of the grid
                if i >= 0 and i < self.size	and j >= 0 and j < self.size:
                    # check that the current cell is different than the assigned one
                    if i != row or j != col:
                        # check that the current cell does not contain a llama or a mine
                        if self.content[i][j].value != self.llama and self.content[i][j].value != self.mine:
                            self.content[i][j].value += counter

    def discover_cells(self, row, col, cells):
        self.content[row][col].clicked = True
        cells.append((row, col, self.content[row][col].value))

        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if i >= 0 and i < self.size	and j >= 0 and j < self.size:
                    if self.content[i][j].clicked == False:
                        if self.content[i][j].value == 0:
                            self.content[i][j].clicked = True
                            self.discover_cells(i, j, cells)
                        elif self.content[i][j].value > 0:
                            self.content[i][j].clicked = True
                            cells.append((i, j, self.content[i][j].value))

        return cells


class GameGrid(object):

    def __init__(self, level):
        size = 1
        nb_llamas = 0
        nb_mines = 0

        if level == 'easy':
            size = 8
            nb_llamas = 3
            nb_mines = 7
        elif level == 'normal':
            size = 12
            nb_llamas = 6
            nb_mines = 15
        elif level == 'hard':
            size = 16
            nb_llamas = 12
            nb_mines = 26

        self.grid = Grid(size, nb_llamas, nb_mines)

    def discover_cell(self, row, column):
        self.grid.content[row][column].clicked = True
        content_cell = self.grid.content[row][column].value

        if content_cell is 0:
            return self.grid.discover_cells(row, column, [])
        elif content_cell is self.grid.llama:
            return 'L'
        elif content_cell is self.grid.mine:
            return 'M'
        else:
            return content_cell
