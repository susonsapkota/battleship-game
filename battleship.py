import random

HIT_CHAR = 'x'
MISS_CHAR = 'o'
BLANK_CHAR = '.'
HORIZONTAL = 'h'
VERTICAL = 'v'
MAX_MISSES = 20
SHIP_SIZES = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2
}
NUM_ROWS = 10
NUM_COLS = 10
ROW_IDX = 0
COL_IDX = 1
MIN_ROW_LABEL = 'A'
MAX_ROW_LABEL = 'J'


def get_random_position():
    """Generates a random location on a board of NUM_ROWS x NUM_COLS."""

    row_choice = chr(
        random.choice(
            range(
                ord(MIN_ROW_LABEL),
                ord(MIN_ROW_LABEL) + NUM_ROWS
            )
        )
    )

    col_choice = random.randint(0, NUM_COLS - 1)

    return (row_choice, col_choice)


def play_battleship():
    """Controls flow of Battleship games including display of
    welcome and goodbye messages.

    :return: None
    """

    print("Let's Play Battleship!\n")

    game_over = False

    while not game_over:

        game = Game()
        game.display_board()

        while not game.is_complete():
            pos = game.get_guess()
            result = game.check_guess(pos)
            game.update_game(result, pos)
            game.display_board()

        game_over = end_program()

    print("Goodbye.")


class Ship:
    def __init__(self, name, start_position, orientation):
        """Creates a new ship with the given name, placed at start_position in the
        provided orientation. The number of positions occupied by the ship is determined
        by looking up the name in the SHIP_SIZE dictionary.
        :param name: the name of the ship
        :param start_position: tuple representing the starting position of ship on the board
        :param orientation: the orientation of the ship ('v' - vertical, 'h' - horizontal)
        :return: None
        """
        self.positions = {}
        self.name = name
        self.hit = ""
        self.sunk = False
        # checking if that ship type is valid
        if name in SHIP_SIZES.keys():
            size = SHIP_SIZES[name]
        else:
            return
        # getting the starting position
        start_row, start_column = start_position

        # if the orientation is horizontal
        if orientation == HORIZONTAL:
            # looping till the size of the ship
            for i in range(size):
                self.positions[(start_row, start_column)] = False
                start_column += 1
        # if the orientation is vertical
        elif orientation == VERTICAL:
            # looping according to the size of the ship
            for i in range(size):
                self.positions[(start_row, start_column)] = False
                # converting A to no, increasing it and converting back
                start_row = chr(ord(start_row) + 1)


class Game:

    _ship_types = ["carrier", "battleship", "cruiser", "submarine", "destroyer"]

    def display_board(self):
        """ Displays the current state of the board."""

        print()
        print("  " + ' '.join('{}'.format(i) for i in range(len(self.board))))
        for row_label in self.board.keys():
            print('{} '.format(row_label) + ' '.join(self.board[row_label]))
        print()

    def __init__(self, max_misses=MAX_MISSES):
        """ Creates a new game with max_misses possible missed guesses.
        The board is initialized in this function and ships are randomly
        placed on the board.
        :param max_misses: maximum number of misses allowed before game ends
        """
        self.max_misses = MAX_MISSES
        self.ships = []
        self.board = {}
        self.guesses = []
        self.initialize_board()
        self.create_and_place_ships()

    def initialize_board(self):
        """Sets the board to it's initial state with each position occupied by
        a period ('.') string.

        :return: None
        """

        start_pos = MIN_ROW_LABEL
        # adding . on all the board
        for i in range(10):
            self.board[start_pos] = ['.'] * 10
            start_pos = chr(ord(start_pos) + 1)

    def in_bounds(self, start_position, ship_size, orientation):
        """Checks that a ship requiring ship_size positions can be placed at start position.

        :param start_position: tuple representing the starting position of ship on the board
        :param ship_size: number of positions needed to place ship
        :param orientation: the orientation of the ship ('v' - vertical, 'h' - horizontal)
        :return status: True if ship placement inside board boundary, False otherwise
        """
        row, col = start_position
        if orientation == HORIZONTAL:
            # col + size should not be greater than no of rows
            if col + ship_size > NUM_COLS:
                return False
            else:
                return True
        elif orientation == VERTICAL:
            # current row + ship size should not exceed 'J'
            if ord(row) + ship_size > ord(MAX_ROW_LABEL):
                return False
            else:
                return True

    def overlaps_ship(self, start_position, ship_size, orientation):
        """Checks for overlap between previously placed ships and a potential new ship
        placement requiring ship_size positions beginning at start_position in the
        given orientation.

        :param start_position: tuple representing the starting position of ship on the board
        :param ship_size: number of positions needed to place ship
        :param orientation: the orientation of the ship ('v' - vertical, 'h' - horizontal)
        :return status: True if ship placement overlaps previously placed ship, False otherwise
        """

        possible_position = {}
        # getting the starting position
        start_row, start_column = start_position

        # creating positions of new ship
        # if the orientation is horizontal
        if orientation == HORIZONTAL:
            # looping till the size of the ship
            for i in range(ship_size):
                possible_position[(start_row, start_column)] = False
                start_column += 1
        # if the orientation is vertical
        elif orientation == VERTICAL:
            # looping according to the size of the ship
            for i in range(ship_size):
                possible_position[(start_row, start_column)] = False
                # converting A to no, increasing it and converting back
                start_row = chr(ord(start_row) + 1)

        # checking possible position is already taken by other ships
        for ship in self.ships:
            ship_pos = ship.positions.keys()
            for pos in possible_position.keys():
                if pos in ship_pos:
                    return True
        # if nothing is in position return true
        return False

    def place_ship(self, start_position, ship_size):
        """Determines if placement is possible for ship requiring ship_size positions placed at
        start_position. Returns the orientation where placement is possible or None if no placement
        in either orientation is possible.

        :param start_position: tuple representing the starting position of ship on the board
        :param ship_size: number of positions needed to place ship
        :return orientation: 'h' if horizontal placement possible, 'v' if vertical placement possible,
        None if no placement possible
        """
        # checking if possible in vertical positions
        if self.in_bounds(start_position, ship_size, 'v') and \
                not self.overlaps_ship(start_position, ship_size, 'v'):
            return 'v'
        # checking if possible in horizontal positions
        elif self.in_bounds(start_position, ship_size, 'h') and \
                not self.overlaps_ship(start_position, ship_size, 'h'):
            return 'h'
        else:
            # if both of the position not available
            return None

    def create_and_place_ships(self):
        """Instantiates ship objects with valid board placements.

        :return: None
        """
        for ship in self._ship_types:
            while True:
                random_pos = get_random_position()
                orient = self.place_ship(random_pos, SHIP_SIZES[ship])
                if orient is not None:
                    myship = Ship(ship, random_pos, orient)
                    self.ships.append(myship)
                    break

    def get_guess(self):
        """Prompts the user for a row and column to attack. The
        return value is a board position in (row, column) format
        :return position: a board position as a (row, column) tuple
        """

        while True:
            row = input("Enter a row: ")[0]
            if ord(MIN_ROW_LABEL) <= ord(row) <= ord(MAX_ROW_LABEL):
                break
        while True:
            col = int(input("Enter a column: "))
            if 0 <= col <= 9:
                break
        return (row, col)

    def check_guess(self, position):
        """Checks whether or not position is occupied by a ship. A hit is
        registered when position occupied by a ship and position not hit
        previously. A miss occurs otherwise.
        :param position: a (row,column) tuple guessed by user
        :return: guess_status: True when guess results in hit, False when guess results in miss
        """
        for ship in self.ships:
            if position in ship.positions.keys() and ship.positions[position] is False:
                ship.positions[position] = True
                all_true = True
                for pos in ship.positions.keys():
                    if not ship.positions[pos]:
                        all_true = False
                        break
                if all_true:
                    ship.sunk = True
                    print(f'You sunk the {ship.name}!')
                return True
        return False

    def update_game(self, guess_status, position):
        """Updates the game by modifying the board with a hit or miss
        symbol based on guess_status of position.
        :param guess_status: True when position is a hit, False otherwise
        :param position: a (row,column) tuple guessed by user
        :return: None
        """
        row, col = position
        value = self.board[row]
        if value[col] == BLANK_CHAR:
            if guess_status:
                # update board to hit
                value[col] = HIT_CHAR
            else:
                # update board and guesses attribute (miss)
                value[col] = MISS_CHAR
                self.guesses.append(position)
        elif not guess_status:
            self.guesses.append(position)
        # if guess_status:
        #     self.board[row][col] = 'x'
        #
        # elif guess_status == False and not self.board[row][col] == 'x':
        #     # not increasing if guess was already in list but it was throwing an error.
        #     self.board[row][col] = 'o'
        #     self.guesses.append(position)

    def is_complete(self):
        """Checks to see if a Battleship game has ended. Returns True when the game is complete
        with a message indicating whether the game ended due to successfully sinking all ships
        or reaching the maximum number of guesses. Returns False when the game is not
        complete.

        :return: True on game completion, False otherwise
        """
        if len(self.guesses) == MAX_MISSES:  # when user reaches max number of guesses
            print("SORRY! NO GUESSES LEFT.")
            return True
        for ship in self.ships:
            if ship.sunk is False:
                return False
        print("YOU WIN!")  # when all ships are sunk
        return True


def end_program():
    """Prompts the user with "Play again (Y/N)?" The question is repeated
    until the user enters a valid response (Y/y/N/n). The function returns
    False if the user enters 'Y' or 'y' and returns True if the user enters
    'N' or 'n'.

    :return response: boolean indicating whether to end the program
    """
    while True:
        play_again = input('Play again (Y/N)?')
        if play_again.lower() == 'n':
            return True
        elif play_again.lower() == 'y':
            return False


def main():
    """Executes one or more games of Battleship."""
    play_battleship()


if __name__ == "__main__":
    main()
