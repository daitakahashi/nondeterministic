
from nondeterministic.interpreter import Interpreter
from nondeterministic.state_tree import StateTree

MAZE = '''
........
--.--+-.
.....|..
.+.|..|.
..-++.|.
|...|...
|.|.|.|.
+-+.+-+.
........
'''.strip()

def maze_to_graph(maze):
    roads = {
        (i, j)
        for i, row in enumerate(maze.split())
        for j, elem in enumerate(list(row))
        if elem == '.'
    }
    graph = {}
    for i, j in roads:
        graph[(i, j)] = {
            (i + x, j + y)
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]
            if (i + x, j + y) in roads
        }
    return graph

def draw_path(location_history, maze):
    maze_ll = [
        list(row) for row in maze.split()
    ]
    for i, j in location_history:
        maze_ll[i][j] = '#'
    for ix, elem in [(0, 'S'), (-1, 'G')]: # mark endpoints
        i, j = location_history[ix]
        maze_ll[i][j] = elem
    return '\n'.join(''.join(row) for row in maze_ll)


# part 1. find paths between two points
def guess_solution(state, graph, goal):
    current = state[-1]
    if current == goal:
        return [state]

    return [
        state + [next_location]
        for next_location in graph[current]
        if next_location not in state
    ]

def test_find_solutions():
    start = (0, 0)
    goal = (8, 0)
    maze_graph = maze_to_graph(MAZE)

    st = StateTree([[start]])
    f = lambda x: guess_solution(x, maze_graph, goal)
    for _ in range(len(maze_graph)): # a simple upper bound
        st.step(f)
    assert {draw_path(sol, MAZE) for sol in st} == {
        expected.strip() for expected in ['''
S##.....
--#--+-.
..###|..
.+.|##|.
..-++#|.
|...|###
|.|.|.|#
+-+.+-+#
G#######
''', '''
S##.....
--#--+-.
###..|..
#+.|..|.
##-++.|.
|###|...
|.|#|.|.
+-+#+-+.
G###....
''', '''
S#######
--.--+-#
.....|.#
.+.|..|#
..-++.|#
|...|..#
|.|.|.|#
+-+.+-+#
G#######
''', '''
S#######
--.--+-#
#####|.#
#+.|##|#
##-++#|#
|###|###
|.|#|.|.
+-+#+-+.
G###....
''']}


# part 2. find paths that satisfy ambiguous trajectory records
def add(x, y):
    return (x[0] + y[0], x[1] + y[1])

def rotate_left(x):
    return (-x[1], x[0])

def rotate_right(x):
    return (x[1], -x[0])

def is_ok(location, graph, hist):
    current = hist[-1]
    return location in graph[current] and location not in hist

def guess_wandering(state, observation, graph):
    location_history, direction = state
    current = location_history[-1]

    # 1. go straight if possible
    # (note: there are no records if it goes straight)
    next_location = add(current, direction)
    if is_ok(next_location, graph, location_history):
        new_state = (location_history + [next_location], direction)
        nexts = guess_wandering(new_state, observation, graph)
    else:
        nexts = []

    # 2. turn left or right according to the observation
    if observation == '?':
        observation = ['left', 'right']
    else:
        observation = [observation]
    for turn in observation:
        if turn == 'left':
            next_direction = rotate_left(direction)
        elif turn == 'right':
            next_direction = rotate_right(direction)
        else:
            raise RuntimeError('unknown turning direction {}'.format(
                turn
            ))
        next_location = add(current, next_direction)
        if is_ok(next_location, graph, location_history):
            nexts.append(
                (location_history + [next_location], next_direction)
            )
    return nexts


def test_maze_wandering():
    turns = [
        'right', '?', '?', '?', '?', 'left', '?', '?', 'left'
    ]
    maze_graph = maze_to_graph(MAZE)
    it = Interpreter(
        lambda x, o: guess_wandering(x, o, maze_graph),
        ([(0, 0)], (0, 1))
    )
    for turn in turns:
        it.interpret(turn)
    assert {draw_path(state[0], MAZE) for state in it} == {
        expected.strip() for expected in ['''
S##.....
--#--+-.
###..|..
#+.|..|.
##-++.|.
|###|...
|.|#|.|.
+-+#+-+G
...#####
''', '''
S#######
--G--+-#
###..|.#
#+.|..|#
##-++.|#
|###|..#
|.|#|.|#
+-+#+-+#
...#####
''']}
