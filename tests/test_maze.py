
from nondeterministic.interpreter import Interpreter

MAZE = '''
........
00.0000.
.....0..
.000..0.
..000.0.
0...0...
0.0.0.0.
000.000.
........
'''.strip()

TURNS = [
    'right', 'right', 'left', 'left', 'right', 'left', 'right', 'left', 'left'
]

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

def draw_path(location_history):
    maze_ll = [
        list(row) for row in MAZE.split()
    ]
    for i, j in location_history:
        maze_ll[i][j] = '#'
    for ix, elem in [(0, 'S'), (-1, 'G')]: # mark endpoints
        i, j = location_history[ix]
        maze_ll[i][j] = elem
    return '\n'.join(''.join(row) for row in maze_ll)

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])

def rotate_left(x):
    return (-x[1], x[0])

def rotate_right(x):
    return (x[1], -x[0])


def guess(state, observation, graph):
    location_history, direction = state
    current = location_history[-1]
    nexts = []

    # 1. go straight if possible
    # (note: there are no records if it goes straight)
    next_location = add(current, direction)
    if next_location in graph[current] \
       and next_location not in location_history:
        new_state = (location_history + [next_location], direction)
        nexts.extend(guess(new_state, observation, graph))

    # 2. turn left or right according to the observation
    if observation == 'left':
        direction = rotate_left(direction)
    elif observation == 'right':
        direction = rotate_right(direction)
    else:
        raise NotImplementedError(
            'unknown direction {}'.format(observation)
        )
    next_location = add(current, direction)
    if next_location in graph[current] \
       and next_location not in location_history:
        nexts.append(
            (location_history + [next_location], direction)
        )
    return nexts


def test_maze_wandering():
    maze_graph = maze_to_graph(MAZE)
    it = Interpreter(
        lambda x, o: guess(x, o, maze_graph),
        ([(0, 0)], (0, 1))
    )
    for turn in TURNS:
        it.interpret(turn)
    assert [draw_path(state[0]) for state in it] == ['''
S##.....
00#0000.
###..0..
#000..0.
##000.0.
0###0...
0.0#0.0.
000#000G
...#####
'''.strip()]
