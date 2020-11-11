from nondeterministic.state_tree import StateTree
from nondeterministic.traversal import dfs

class Board:
    def __init__(self, known=None, unknown=None):
        if not known:
            known = {}
        if not unknown:
            unknown = {
                (i, j): list(range(9))
                for i in range(9)
                for j in range(9)
            }
        self.known = known
        self.unknown = unknown

    def choose_next_ix(self):
        v = [(ix, len(vs)) for ix, vs in self.unknown.items()]
        return min(v, key=lambda x: x[1])[0]

    def set(self, i, j, value):
        self.known[(i, j)] = value
        self.unknown.pop((i, j), None)

    def forget(self, i, j, value):
        if (i, j) in self.unknown:
            self.unknown[(i, j)] = [
                v for v in self.unknown[(i, j)]
                if v != value
            ]

    def is_unsatisfiable(self):
        return any(len(vs) < 1 for vs in self.unknown.values())

    def is_completed(self):
        return len(self.unknown) == 0


def block_indices(i, j):
    block_0i, block_0j = 3*(i//3), 3*(j//3)
    return [
            (k + block_0i, l + block_0j)
            for k in range(3) for l in range(3)
    ]


def assume(prev, i, j, value):
    b = Board(prev.known.copy(), prev.unknown.copy())
    # (1) set (i, j)
    b.set(i, j, value)
    # (2) remove the value from the row and the column
    for x in range(9):
        if x != i:
            b.forget(x, j, value)
        if x != j:
            b.forget(i, x, value)
    # (3) remove the value from the block
    for x, y in block_indices(i, j):
        if (x, y) != (i, j):
            b.forget(x, y, value)
    return b


def apply_problem(knowns):
    b = Board()
    for (i, j), value in knowns.items():
        b = assume(b, i, j, value)
    return b


def guess(b):
    if b.is_unsatisfiable():
        return []
    if b.is_completed():
        return [b]
    ix = b.choose_next_ix()
    values = b.unknown[ix]
    return [
        assume(b, *ix, value) for value in values
    ]


def encode(board2d):
    result = {}
    for i, row in enumerate(board2d):
        for j, val in enumerate(row):
            if val != 0:
                result[(i, j)] = val - 1
    return result


def decode(b):
    result = []
    for _ in range(9):
        result.append([0]*9)
    for (i, j), value in b.known.items():
        result[i][j] = value + 1
    return result


def sudoku_solver(problem):
    b = apply_problem(encode(problem))
    st = StateTree([b], dfs())
    for _ in range(len(b.unknown)):
        st.step(guess)
    return decode(st.current)


# a sudoku problem from: https://ja.wikipedia.org/wiki/%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB:Sudoku-by-L2G-20050714.svg
def test_solve_sudoku():
    prob = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    solution = sudoku_solver(prob)
    assert solution == [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
