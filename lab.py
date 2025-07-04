"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import
# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    height = len(level_description)
    width = len(level_description[0])
    player_coordinates = ()
    computers_in_targets = 0
    computers = set()
    targets = set()
    walls = set()
    for row in range(height):
        for col in range(width):
            box = level_description[row][col]
            if "player" in box:
                player_coordinates = row, col
            if "target" in box:
                targets.add((row, col))
                if "computer" in box:
                    computers_in_targets += 1
            if "computer" in box:
                computers.add((row, col))
            if "wall" in box:
                walls.add((row, col))
    assert player_coordinates, "Player coordinates not found"
    return {
        "height": height,
        "width": width,
        "player_coords": player_coordinates,
        "computers": computers,
        "computers_in_targets": computers_in_targets,
        "targets": targets,
        "walls": walls,
    }


def deepcopy_game(game):
    """
    Returns a deep copy of the game dictionary
    """
    return {
        "height": game["height"],
        "width": game["width"],
        "player_coords": game["player_coords"],
        "computers": game["computers"].copy(),
        "computers_in_targets": game["computers_in_targets"],
        "targets": game["targets"],
        "walls": game["walls"],
    }


def move_player(game, direction):
    """
    Moves the player to a new destination in the direction given
    game: a python dictionary representing the game board returned from
        make_new_game
    direction: a string showing the direction either 'up', 'down', 'left'
        or 'right'

    Returns a new dictionary of the resulting game board
    """
    new_game = deepcopy_game(game)
    dest = find_dest(game, direction)[0]
    new_game["player_coords"] = dest
    return new_game


def move_computer(game, direction):
    """
    Moves the computer to a new destination in the direction given
    game: a python dictionary representing the game board returned from
        make_new_game
    direction: a string showing the direction either 'up', 'down', 'left'
        or 'right'

    Returns a new dictionary of the resulting game board
    """
    new_game = deepcopy_game(game)
    dest_1, dest_2 = find_dest(game, direction)
    new_game["computers"].remove(dest_1)
    if dest_1 in new_game["targets"]:
        new_game["computers_in_targets"] -= 1
    new_game["computers"].add(dest_2)
    if dest_2 in new_game["targets"]:
        new_game["computers_in_targets"] += 1
    return new_game


def find_dest(game, direction):
    """
    Given the direction return the next two destinations that a player
    and computer would move to.
    game: a python dictionary representing the game board returned from
        make_new_game
    direction: a string showing the direction either 'up', 'down', 'left'
        or 'right'
    """
    old_coords = game["player_coords"]
    change = DIRECTION_VECTOR[direction]
    dest_1 = old_coords[0] + change[0], old_coords[1] + change[1]
    dest_2 = old_coords[0] + 2 * change[0], old_coords[1] + 2 * change[1]
    return dest_1, dest_2


def check_valid_dest(game, coords):
    if coords in game["walls"] or coords in game["computers"]:
        return False
    return True


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    return (
        game["computers_in_targets"] == len(game["computers"])
        and len(game["computers"]) > 0
    )


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    dest_1, dest_2 = find_dest(game, direction)
    if check_valid_dest(game, dest_1):
        return move_player(game, direction)
    else:
        if dest_1 in game["computers"]:
            if check_valid_dest(game, dest_2):
                new_game = move_computer(game, direction)
                return move_player(new_game, direction)
    return game


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    player = game["player_coords"]
    height = game["height"]
    width = game["width"]
    board = [[[] for _ in range(width)] for _ in range(height)]
    for row, col in game["walls"]:
        board[row][col].append("wall")
    for row, col in game["computers"]:
        board[row][col].append("computer")
    for row, col in game["targets"]:
        board[row][col].append("target")
    board[player[0]][player[1]].append("player")
    return board


def check_if_move_valid(game, direction):
    """
    Given a direction, return True if it is possible for the player to move
    in that direction.
    """
    dest_1, dest_2 = find_dest(game, direction)
    if check_valid_dest(game, dest_1):
        return True
    else:
        if dest_1 in game["computers"]:
            if check_valid_dest(game, dest_2):
                return True
    return False


def get_state(game):
    """
    Given a game representation, return a hashable tuple representing the game
    """
    return (
        game["player_coords"],
        frozenset(game["computers"]),
        game["computers_in_targets"],
    )


def get_game(state, original_game):
    """
    Given a state representation and the original game, return a game representation
    that is representated from the state.

    state: a hashable tuple returned from get_state
    """
    player_coords, computers_set, computers_in_targets = state
    return {
        "height": original_game["height"],
        "width": original_game["width"],
        "player_coords": player_coords,
        "computers": set(computers_set),
        "computers_in_targets": computers_in_targets,
        "targets": original_game["targets"],
        "walls": original_game["walls"],
    }


def win_test(state):
    """
    Given a state, determine whether the winning condition is satisified
    """
    return len(state[1]) == state[2]


def next_possible_states(state, original_game):
    """
    Given a state, return all the possible states that can reached from this state.
    """
    next_games = []
    current_game = get_game(state, original_game)
    for direction in DIRECTION_VECTOR:
        if not direction:
            print("There is something wrong here")
        if check_if_move_valid(current_game, direction):
            next_games.append(step_game(current_game, direction))
    return [get_state(game) for game in next_games]


def get_connecting_move(state1, state2):
    """
    Given two states, return s string of the direction in which the player would
    move to go from the first state to the second.
    """
    player_pos_1, player_pos_2 = state1[0], state2[0]
    change = player_pos_2[0] - player_pos_1[0], player_pos_2[1] - player_pos_1[1]
    for direction, vector in DIRECTION_VECTOR.items():
        if vector == change:
            return direction
    assert False, "No direction found connecting these two states"


def solve_puzzle_states(game):
    """
    Given a game representation, return a list of states that a player can make
    until they have solved the puzzle.

    Return None if it is impossible to solve the puzzle.
    """
    start_state = get_state(game)
    if win_test(start_state):
        return []
    agenda = [[start_state]]
    visited = {start_state}

    while agenda:
        path = agenda.pop(0)
        last_state = path[-1]
        for state in next_possible_states(last_state, game):
            if state in visited:
                continue
            new_path = path + [state]
            if win_test(state):
                return new_path
            agenda.append(new_path)
            visited.add(state)

    return None


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    path = solve_puzzle_states(game)
    if path is None:
        return None
    return [
        get_connecting_move(state1, state2) for state1, state2 in zip(path, path[1:])
    ]


if __name__ == "__main__":
    # with open('puzzles/m1_032.json') as f:
    #     game = json.load(f)

    # transformed = make_new_game(game)
    # print(solve_puzzle(transformed))
    pass
