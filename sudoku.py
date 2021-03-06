def getel(s):
    """Returns the unique element in a singleton set (or list)."""
    assert len(s) == 1
    return list(s)[0]

import json

class Sudoku(object):

    def __init__(self, elements):
        """Elements can be one of:
        Case 1: a list of 9 strings of length 9 each.
        Each string represents a row of the initial Sudoku puzzle,
        with either a digit 1..9 in it, or with a blank or _ to signify
        a blank cell.
        Case 2: an instance of Sudoku.  In that case, we initialize an
        object to be equal (a copy) of the one in elements.
        Case 3: a list of list of sets, used to initialize the problem."""
        if isinstance(elements, Sudoku):
            # We let self.m consist of copies of each set in elements.m
            self.m = [[x.copy() for x in row] for row in elements.m]
        else:
            assert len(elements) == 9
            for s in elements:
                assert len(s) == 9
            # We let self.m be our Sudoku problem, a 9x9 matrix of sets.
            self.m = []
            for s in elements:
                row = []
                for c in s:
                    if isinstance(c, str):
                        if c.isdigit():
                            row.append({int(c)})
                        else:
                            row.append({1, 2, 3, 4, 5, 6, 7, 8, 9})
                    else:
                        assert isinstance(c, set)
                        row.append(c)
                self.m.append(row)


    def show(self, details=False):
        """Prints out the Sudoku matrix.  If details=False, we print out
        the digits only for cells that have singleton sets (where only
        one digit can fit).  If details=True, for each cell, we display the
        sets associated with the cell."""
        if details:
            print("+-----------------------------+-----------------------------+-----------------------------+")
            for i in range(9):
                r = '|'
                for j in range(9):
                    # We represent the set {2, 3, 5} via _23_5____
                    s = ''
                    for k in range(1, 10):
                        s += str(k) if k in self.m[i][j] else '_'
                    r += s
                    r += '|' if (j + 1) % 3 == 0 else ' '
                print(r)
                if (i + 1) % 3 == 0:
                    print("+-----------------------------+-----------------------------+-----------------------------+")
        else:
            print("+---+---+---+")
            for i in range(9):
                r = '|'
                for j in range(9):
                    if len(self.m[i][j]) == 1:
                        r += str(getel(self.m[i][j]))
                    else:
                        r += "."
                    if (j + 1) % 3 == 0:
                        r += "|"
                print(r)
                if (i + 1) % 3 == 0:
                    print("+---+---+---+")


    def to_string(self):
        """This method is useful for producing a representation that
        can be used in testing."""
        as_lists = [[list(self.m[i][j]) for j in range(9)] for i in range(9)]
        return json.dumps(as_lists)


    @staticmethod
    def from_string(s):
        """Inverse of above."""
        as_lists = json.loads(s)
        as_sets = [[set(el) for el in row] for row in as_lists]
        return Sudoku(as_sets)


    def __eq__(self, other):
        """Useful for testing."""
        return self.m == other.m

class Unsolvable(Exception):
    pass


def sudoku_ruleout(self, i, j, x):
    """The input consists in a cell (i, j), and a value x.
    The function removes x from the set self.m[i][j] at the cell, if present, and:
    - if the result is empty, raises Unsolvable;
    - if the cell used to be a non-singleton cell and is now a singleton
      cell, then returns the set {(i, j)};
    - otherwise, returns the empty set."""
    c = self.m[i][j]
    n = len(c)
    c.discard(x)
    self.m[i][j] = c
    if len(c) == 0:
        raise Unsolvable()
    return {(i, j)} if 1 == len(c) < n else set()

Sudoku.ruleout = sudoku_ruleout

def sudoku_propagate_cell(self, ij):
    """Propagates the singleton value at cell (i, j), returning the list
    of newly-singleton cells."""
    i, j = ij
    if len(self.m[i][j]) > 1:
        # Nothing to propagate from cell (i,j).
        return set()
    # We keep track of the newly-singleton cells.
    newly_singleton = set()
    x = getel(self.m[i][j]) # Value at (i, j).
    # Same row.
    for jj in range(9):
        if jj != j: # Do not propagate to the element itself.
            newly_singleton.update(self.ruleout(i, jj, x))
    # Same column.
    ### YOUR CODE HERE
    for ii in range(9):
        if ii != i: # Do not propagate to the element itself.
            newly_singleton.update(self.ruleout(ii, j, x))
    # Same block of 3x3 cells.
    subrow = i//3
    subcol = j//3
    for col in range(subcol*3, subcol*3 + 3):
        for row in range(subrow*3, subrow*3 + 3):
            if row != i and col != j:
                newly_singleton.update(self.ruleout(row, col, x))

    ### YOUR CODE HERE
    # Returns the list of newly-singleton cells.
    return newly_singleton

Sudoku.propagate_cell = sudoku_propagate_cell

def sudoku_propagate_all_cells_once(self):
    """This function propagates the constraints from all singletons."""
    for i in range(9):
        for j in range(9):
            self.propagate_cell((i, j))

Sudoku.propagate_all_cells_once = sudoku_propagate_all_cells_once

def sudoku_full_propagation(self, to_propagate=None):
    """Iteratively propagates from all singleton cells, and from all
    newly discovered singleton cells, until no more propagation is possible.
    @param to_propagate: sets of cells from where to propagate.  If None, propagates
        from all singleton cells. 
    @return: nothing.
    """
    if to_propagate is None:
        to_propagate = {(i, j) for i in range(9) for j in range(9)}
    # This code is the (A) code; will be referenced later.
    ### YOUR CODE HERE
    while len(to_propagate) > 0:
        u = to_propagate.pop()
        to_propagate.update(self.propagate_cell(u))


Sudoku.full_propagation = sudoku_full_propagation

def sudoku_done(self):
    """Checks whether an instance of Sudoku is solved."""
    for i in range(9):
        for j in range(9):
            if len(self.m[i][j]) > 1:
                return False
    return True

Sudoku.done = sudoku_done


def sudoku_search(self, new_cell=None):
    """Tries to solve a Sudoku instance."""
    to_propagate = None if new_cell is None else {new_cell}
    self.full_propagation(to_propagate=to_propagate)
    if self.done():
        return self # We are a solution
    # We need to search.  Picks a cell with as few candidates as possible.
    candidates = [(len(self.m[i][j]), i, j)
                   for i in range(9) for j in range(9) if len(self.m[i][j]) > 1]
    _, i, j = min(candidates)
    values = self.m[i][j]
    # values contains the list of values we need to try for cell i, j.
    # print("Searching values", values, "for cell", i, j)
    for x in values:
        # print("Trying value", x)
        sd = Sudoku(self)
        sd.m[i][j] = {x}
        try:
            # If we find a solution, we return it.
            return sd.search(new_cell=(i, j))
        except Unsolvable:
            # Go to next value.
            pass
    # All values have been tried, apparently with no success.
    raise Unsolvable()

Sudoku.search = sudoku_search


def sudoku_solve(self, do_print=True):
    """Wrapper function, calls self and shows the solution if any."""
    try:
        r = self.search()
        if do_print:
            print("We found a solution:")
            r.show()
    except Unsolvable:
        if do_print:
            print("The problem has no solutions")

Sudoku.solve = sudoku_solve