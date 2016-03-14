from random import randint

class Cell(object):

	value = 0
	clicked = False

class Grid(object):

	def __init__(self, size):
		"""Constructor: creates a grid of of size "size" containing 0 on each cell"""

		self.size = size
		self.grid = []
		self.llama = -1
		self.mine = -2

		for i in range(self.size):
			row = []
			for j in range(self.size):
				row.append(Cell())
			self.grid.append(row)


	def print_grid(self):
		"""prints the grid's cells"""
		for i in range(self.size):
			for j in range(self.size):
				if self.grid[i][j].clicked == True:
					print "%s" % (str(self.grid[i][j].value)),
				else:
					print("*"),
			print
		print


	def place_item(self, item, amount, is_llama):
		"""Generates random coordinates to place llamas or mines on the grid"""
		placed = 0

		while placed < amount:
			row = randint(0, self.size-1)
			col = randint(0, self.size-1)
			if self.grid[row][col].value != self.llama and self.grid[row][col].value != self.mine:
				self.grid[row][col].value = item
				self.set_other_cells(row, col, is_llama)
				placed += 1


	"""Counts the number of llamas or mines placed around each cell"""
	def set_other_cells(self, row, col, is_llama):
		counter = 1
		if is_llama:
			counter = 10

		#go to each cell surrounding the current cell
		for i in range(row-1, row+2):
			for j in range(col-1, col+2):

				# check that the index is within the size of the grid
				if i >= 0 and i < self.size	and j >= 0 and j < self.size:
					# check that the current cell is different than the assigned one
					if i != row or j != col:
						# check that the current cell does not contain a llama or a mine
						if self.grid[i][j].value != self.llama and self.grid[i][j].value != self.mine:
							self.grid[i][j].value += counter
							
	def discover_cells(self, row, col):
		self.grid[row][col].clicked = True

		for i in range(row-1, row+2):
			for j in range(col-1, col+2):
				if i >= 0 and i < self.size	and j >= 0 and j < self.size:
					if self.grid[i][j].clicked == False:
						if self.grid[i][j].value == 0:
							self.grid[i][j].clicked = True
							self.discover_cells(i, j)
						elif self.grid[i][j].value > 0:
							self.grid[i][j].clicked = True


grid = Grid(8)
grid.print_grid()
grid.place_item(grid.llama, 3, True)
grid.place_item(grid.mine, 7, False)
grid.grid[4][3].clicked = True
if grid.grid[4][3].value == 0:
	grid.discover_cells(4,3)
grid.print_grid()