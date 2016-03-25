from random import randint


class Cell(object):

    def __init__(self):
        self.value = 0
        self.clicked = False


class GameGrid(object):
    size = 0
    grid = []
    llama = 'L'
    mine = 'M'
    nb_llamas = 0
    nb_mines = 0

    def __init__(self, level):
        """Constructor: creates a grid of of level "level" containing 0 on each cell."""
        self.grid = []

        # set the size and the number of llamas and mines of the grid,
        # depending on the level of the game
        if level == 'easy':
            self.size = 8
            self.nb_llamas = 3
            self.nb_mines = 8
        elif level == 'normal':
            self.size = 12
            self.nb_llamas = 6
            self.nb_mines = 20
        elif level == 'hard':
            self.size = 16
            self.nb_llamas = 12
            self.nb_mines = 36

        # create Cell on each row and column of the grid
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(Cell())
            self.grid.append(row)

        # place llamas and mines
        self.place_item(item=self.llama, amount=self.nb_llamas, is_llama=True)
        self.place_item(item=self.mine, amount=self.nb_mines, is_llama=False)

    def place_item(self, item, amount, is_llama):
        """Generates random coordinates to place llamas or mines on the grid."""
        placed = 0

        while placed < amount:
            # generate random coordinates
            row = randint(0, self.size-1)
            col = randint(0, self.size-1)

            if 0 <= row < self.size and 0 <= col < self.size:
                # check that the current cell hasn't been assigned to a llama or a mine already
                if self.grid[row][col].value != self.llama and self.grid[row][col].value != self.mine:
                    self.grid[row][col].value = item

                    # update the content of the cells surrounding the current one
                    self.set_other_cells(row=row, col=col, is_llama=is_llama)
                    placed += 1

    def set_other_cells(self, row, col, is_llama):
        """Counts the number of llamas or mines placed around each cell."""
        counter = 1
        if is_llama:
            counter = 10

        # go to each cell surrounding the assigned cell
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):

                # check that the index is within the size of the grid
                if 0 <= i < self.size and 0 <= j < self.size:

                    # check that the current cell is different than the assigned one
                    if i != row or j != col:

                        # check that the current cell does not contain a llama or a mine
                        if self.grid[i][j].value != self.llama and self.grid[i][j].value != self.mine:

                            # update the content of the current cell
                            self.grid[i][j].value += counter

    def click_cell(self, row, col):
        """Returns data from the grid when a cell is clicked on."""
        self.grid[row][col].clicked = True

        # content of the cell that was clicked on
        content_cell = self.grid[row][col].value

        if content_cell is 0:
            # return all the cells that were discovered
            return self.discover_cells(row=row, col=col, cells=[])
        else:
            # return the content of the cell
            return content_cell

    def discover_cells(self, row, col, cells):
        """When a cell containing 0 is clicked, expands the area
        to clear all empty cells close by, and returns all the cells revealed in the process."""
        self.grid[row][col].clicked = True

        # list of cells that were revealed
        cells.append((row, col, self.grid[row][col].value))

        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if 0 <= i < self.size and 0 <= j < self.size:

                    # if the current cell was clicked, there is no need to discover it again
                    if not self.grid[i][j].clicked:

                        # if the current cell is empty, reveal it, and expand the zone around it
                        if self.grid[i][j].value == 0:
                            self.grid[i][j].clicked = True
                            self.discover_cells(row=i, col=j, cells=cells)

                        # if the current cell is not empty, and not a llama or a mine,
                        # reveal it and add it to the list, but do not expand the zone around it
                        elif self.grid[i][j].value > 0:
                            self.grid[i][j].clicked = True
                            cells.append((i, j, self.grid[i][j].value))

        return cells

    def get_unclicked_cells(self):
        """Returns a list of all the cells that have not been clicked on at the end of the game."""
        cells = []

        for i in range(self.size):
            for j in range(self.size):

                if not self.grid[i][j].clicked:
                    cells.append((i, j, self.grid[i][j].value))

        return cells