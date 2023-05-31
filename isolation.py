from argparse import ArgumentError
from copy import deepcopy
import time
import platform
# import io
from io import StringIO

# import resource
if platform.system() != 'Windows':
    import resource

import sys
import os

sys.path[0] = os.getcwd()


class Board:
    BLANK = " "
    BLOCKED = "X"
    TRAIL = "O"
    NOT_MOVED = (-1, -1)

    def __init__(self, player_1, player_2, width=9, height=9):
        self.width = width
        self.height = height

        self.__player_1__ = player_1
        self.__player_2__ = player_2

        self.__queen_1__ = player_1.__class__.__name__ + " - Q1"
        self.__queen_2__ = player_2.__class__.__name__ + " - Q2"

        self.__queen_symbols__ = {self.__queen_1__: "Q1", self.__queen_2__: "Q2"}

        self.__board_state__ = [[Board.BLANK for i in range(0, width)] for j in range(0, height)]

        self.__last_queen_move__ = {self.__queen_1__: Board.NOT_MOVED, self.__queen_2__: Board.NOT_MOVED}

        self.__active_player__ = player_1
        self.__inactive_player__ = player_2
        self.__active_players_queen__ = self.__queen_1__
        self.__inactive_players_queen__ = self.__queen_2__

        self.move_count = 0

    def get_state(self):
        """
        Get physical board state
        Parameters:
            None
        Returns: 
            State of the board: list[char]
        """
        return deepcopy(self.__board_state__)

    def set_state(self, board_state, p1_turn=True):
        '''
        Function to immediately bring a board to a desired state. Useful for testing purposes; call board.play_isolation() afterwards to play
        Parameters:
            board_state: list[str], Desired state to set to board
            p1_turn: bool, Flag to determine which player is active
        Returns:
            None
        '''
        self.__board_state__ = board_state

        queen_1_symbol = self.__queen_symbols__[self.__queen_1__]
        last_move_q1 = [(column, row.index(queen_1_symbol)) for column, row in enumerate(board_state) if queen_1_symbol in row]
        if last_move_q1 != []:
            # set last move to the first found occurance of 'Q1'
            self.__last_queen_move__[self.__queen_1__] = last_move_q1[0]
        else:
            self.__last_queen_move__[self.__queen_1__] = Board.NOT_MOVED

        queen_2_symbol = self.__queen_symbols__[self.__queen_2__]
        last_move_q2 = [(column, row.index(queen_2_symbol)) for column, row in enumerate(board_state) if queen_2_symbol in row]
        if last_move_q2 != []:
            self.__last_queen_move__[self.__queen_2__] = last_move_q2[0]
        else:
            self.__last_queen_move__[self.__queen_2__] = Board.NOT_MOVED

        if p1_turn:
            self.__active_player__ = self.__player_1__
            self.__active_players_queen__ = self.__queen_1__
            self.__inactive_player__ = self.__player_2__
            self.__inactive_players_queen__ = self.__queen_2__

        else:
            self.__active_player__ = self.__player_2__
            self.__active_players_queen__ = self.__queen_2__
            self.__inactive_player__ = self.__player_1__
            self.__inactive_players_queen__ = self.__queen_1__
        # Count X's to get move count + 2 for initial moves
        self.move_count = sum(row.count('X') + row.count('Q1') + row.count('Q2') for row in board_state)

    #function to edit to introduce any variant - edited for impact crater variant by Matthew Zhou (1/23/2023)
    def __apply_move__(self, queen_move):
        '''
        Apply chosen move to a board state and check for game end
        Parameters:
            queen_move: (int, int), Desired move to apply. Takes the 
            form of (column, row). Move must be legal.
        Returns:
            result: (bool, str), Game Over flag, winner 
        '''
        # print("Applying move:: ", queen_move)
        col, row = queen_move
        my_pos = self.__last_queen_move__[self.__active_players_queen__]
        #opponent_pos = self.__last_queen_move__[self.__inactive_players_queen__]

        ######Change the following lines to introduce any variant######
        if my_pos != Board.NOT_MOVED:
            self.__board_state__[my_pos[0]][my_pos[1]] = Board.BLOCKED
        
            #check if queen moves more than 1 space in any direction
            if abs(col - my_pos[0]) > 1 or abs(row - my_pos[1]) > 1:
                self.__create_crater__(queen_move)
       ######Change above lines to introduce any variant######
        
        # apply move of active player
        self.__last_queen_move__[self.__active_players_queen__] = queen_move
        self.__board_state__[col][row] = self.__queen_symbols__[self.__active_players_queen__]


        # rotate the players
        self.__active_player__, self.__inactive_player__ = self.__inactive_player__, self.__active_player__

        # rotate the queens
        self.__active_players_queen__, self.__inactive_players_queen__ = self.__inactive_players_queen__, self.__active_players_queen__

        # increment move count
        self.move_count = self.move_count + 1

        # If opponent is isolated
        if not self.get_active_moves():
            return True, self.__inactive_players_queen__

        return False, None

    #function for impact crater variant only
    def __create_crater__(self, queen_move):
        '''
        Create impact crater - 4 spaces (vertical, horizontal) adjacent to move
        Parameters:
            queen_move: (int, int), Desired move to apply. Takes the 
            form of (column, row).
        Returns:
            None
        '''
        col, row = queen_move
        impact_crater = [(col - 1, row), (col, row - 1), (col, row + 1), (col + 1, row)]
        for adj_col, adj_row in impact_crater:
            if self.move_is_in_board(adj_col, adj_row):
                if self.__board_state__[adj_col][adj_row] == Board.BLANK:
                    self.__board_state__[adj_col][adj_row] = Board.BLOCKED

    def copy(self):
        '''
        Create a copy of this board and game state.
        Parameters:
            None
        Returns:
            Copy of self: Board class
        '''
        b = Board(self.__player_1__, self.__player_2__,
                  width=self.width, height=self.height)
        for key, value in self.__last_queen_move__.items():
            b.__last_queen_move__[key] = value
        for key, value in self.__queen_symbols__.items():
            b.__queen_symbols__[key] = value
            
        b.__board_state__ = self.get_state()
        b.__active_player__ = self.__active_player__
        b.__inactive_player__ = self.__inactive_player__
        b.__active_players_queen__ = self.__active_players_queen__
        b.__inactive_players_queen__ = self.__inactive_players_queen__
        b.move_count = self.move_count

        return b

    def forecast_move(self, queen_move):
        """
        See what board state would result from making a particular move without changing the board state itself.
        Parameters:
            queen_move: (int, int), Desired move to forecast. Takes the form of
            (column, row).

        Returns:
            (Board, bool, str): Resultant board from move, flag for game-over, winner (if game is over)
        """
        new_board = self.copy()
        is_over, winner = new_board.__apply_move__(queen_move)
        return new_board, is_over, winner

    def get_active_player(self):
        """
        See which player is active. Used mostly in play_isolation for display purposes.
        Parameters:
            None
        Returns:
            str: Name of the player who's actively taking a turn
        """
        return self.__active_player__

    def get_inactive_player(self):
        """
        See which player is inactive. Used mostly in play_isolation for display purposes.
        Parameters:
            None
        Returns:
            str: Name of the player who's waiting for opponent to take a turn
        """
        return self.__inactive_player__

    def get_active_players_queen(self):
        """
        See which queen is inactive. Used mostly in play_isolation for display purposes.
        Parameters:
            None
        Returns:
            str: Queen name of the player who's waiting for opponent to take a turn
        """
        return self.__active_players_queen__

    def get_inactive_players_queen(self):
        """
        See which queen is inactive. Used mostly in play_isolation for display purposes.
        Parameters:
            None
        Returns:
            str: Queen name of the player who's waiting for opponent to take a turn
        """
        return self.__inactive_players_queen__

    def get_inactive_position(self):
        """
        Get position of inactive player (player waiting for opponent to make move) in [column, row] format
        Parameters:
            None
        Returns:
           [int, int]: [col, row] of inactive player
        """
        return self.__last_queen_move__[
                   self.__inactive_players_queen__][0:2]

    def get_active_position(self):
        """
        Get position of active player (player actively making move) in [column, row] format
        Parameters:
            None
        Returns:
           [int, int]: [col, row] of active player
        """
        return self.__last_queen_move__[
                   self.__active_players_queen__][0:2]

    def get_player_position(self, my_player=None):
        """
        Get position of certain player object. Should pass in yourself to get your position.
        Parameters:
            my_player (Player), Player to get position for
            If calling from within a player class, my_player = self can be passed.
        returns
            [int, int]: [col, row] position of player

        """
        if (my_player == self.__player_1__ and self.__active_player__ == self.__player_1__):
            return self.get_active_position()
        if (my_player == self.__player_1__ and self.__active_player__ != self.__player_1__):
            return self.get_inactive_position()
        elif (my_player == self.__player_2__ and self.__active_player__ == self.__player_2__):
            return self.get_active_position()
        elif (my_player == self.__player_2__ and self.__active_player__ != self.__player_2__):
            return self.get_inactive_position()
        else:
            raise ValueError("No value for my_player!")

    def get_opponent_position(self, my_player=None):
        """
        Get position of my_player's opponent.
        Parameters:
            my_player (Player), Player to get opponent's position
            If calling from within a player class, my_player = self can be passed.
        returns
            [int, int]: [col, row] position of my_player's opponent

        """
        if (my_player == self.__player_1__ and self.__active_player__ == self.__player_1__):
            return self.get_inactive_position()
        if (my_player == self.__player_1__ and self.__active_player__ != self.__player_1__):
            return self.get_active_position()
        elif (my_player == self.__player_2__ and self.__active_player__ == self.__player_2__):
            return self.get_inactive_position()
        elif (my_player == self.__player_2__ and self.__active_player__ != self.__player_2__):
            return self.get_active_position()
        else:
            raise ValueError("No value for my_player!")

    def get_inactive_moves(self):
        """
        Get all legal moves of inactive player on current board state as a list of possible moves.
        Parameters:
            None
        Returns:
           [(int, int)]: List of all legal moves. Each move takes the form of
            (column, row).
        """
        q_move = self.__last_queen_move__[
            self.__inactive_players_queen__]

        return self.__get_moves__(q_move)

    def get_active_moves(self):
        """
        Get all legal moves of active player on current board state as a list of possible moves.
        Parameters:
            None
        Returns:
           [(int, int)]: List of all legal moves. Each move takes the form of
            (column, row).
        """
        q_move = self.__last_queen_move__[
            self.__active_players_queen__]


        return self.__get_moves__(q_move)

    def get_player_moves(self, my_player=None):
        """
        Get all legal moves of certain player object. Should pass in yourself to get your moves.
        Parameters:
            my_player (Player), Player to get moves for
            If calling from within a player class, my_player = self can be passed.
        returns
            [(int, int)]: List of all legal moves. Each move takes the form of
            (column, row).

        """
        if (my_player == self.__player_1__ and self.__active_player__ == self.__player_1__):
            return self.get_active_moves()
        if (my_player == self.__player_1__ and self.__active_player__ != self.__player_1__):
            return self.get_inactive_moves()
        elif (my_player == self.__player_2__ and self.__active_player__ == self.__player_2__):
            return self.get_active_moves()
        elif (my_player == self.__player_2__ and self.__active_player__ != self.__player_2__):
            return self.get_inactive_moves()
        else:
            raise ValueError("No value for my_player!")

    def get_opponent_moves(self, my_player=None):
        """
        Get all legal moves of the opponent of the player provided. Should pass in yourself to get your opponent's moves.
        If calling from within a player class, my_player = self can be passed.
        Parameters:
            my_player (Player), The player facing the opponent in question
            If calling from within a player class, my_player = self can be passed.
        returns
            [(int, int)]: List of all opponent's moves. Each move takes the form of
            (column, row).

        """
        if (my_player == self.__player_1__ and self.__active_player__ == self.__player_1__):
            return self.get_inactive_moves()
        if (my_player == self.__player_1__ and self.__active_player__ != self.__player_1__):
            return self.get_active_moves()
        elif (my_player == self.__player_2__ and self.__active_player__ == self.__player_2__):
            return self.get_inactive_moves()
        elif (my_player == self.__player_2__ and self.__active_player__ != self.__player_2__):
            return self.get_active_moves()
        else:
            raise ValueError("No value for my_player!")

    def __get_moves__(self, move):
        """
        Get all legal moves of a player on current board state as a list of possible moves. Not meant to be directly called, 
        use get_active_moves or get_inactive_moves instead.
        Parameters:
            move: (int, int), Last move made by player in question (where they currently are). 
            Takes the form of (column, row).
        Returns:
           [(int, int)]: List of all legal moves. Each move takes the form of
            (column, row).
        """

        if move == self.NOT_MOVED:
            return self.get_first_moves()

        c, r = move

        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        moves = []

        for direction in directions:
            for dist in range(1, max(self.height, self.width)):
                col = direction[0] * dist + c
                row = direction[1] * dist + r
                if self.move_is_in_board(col, row) and self.is_spot_open(col, row) and (col, row) not in moves:
                    moves.append((col, row))

                else:
                    break

        return moves

    def get_first_moves(self):
        """
        Return all moves for first turn in game (i.e. every board position)
        Parameters:
            None
        Returns:
           [(int, int)]: List of all legal moves. Each move takes the form of
            (column, row).
        """
        return [(i, j) for i in range(0, self.height)
                for j in range(0, self.width) if self.__board_state__[i][j] == Board.BLANK]

    def move_is_in_board(self, col, row):
        """
        Sanity check for making sure a move is within the bounds of the board.
        Parameters:
            col: int, Column position of move in question
            row: int, Row position of move in question
        Returns:
            bool: Whether the [col, row] values are within valid ranges
        """
        return 0 <= col < self.height and 0 <= row < self.width

    def is_spot_open(self, col, row):
        """
        Sanity check for making sure a move isn't occupied by an X.
        Parameters:
            col: int, Column position of move in question
            row: int, Row position of move in question
        Returns:
            bool: Whether the [col, row] position is blank (no X)
        """
        return self.__board_state__[col][row] == Board.BLANK

    def is_spot_queen(self, col, row):
        """
        Sanity check for checking if a spot is occupied by a player
        Parameters:
            col: int, Column position of move in question
            row: int, Row position of move in question
        Returns:
            bool: Whether the [col, row] position is currently occupied by a player's queen
        """
        q1 = self.__queen_symbols__[self.__active_players_queen__]
        q2 = self.__queen_symbols__[self.__inactive_players_queen__]
        return self.__board_state__[col][row] == q1 or self.__board_state__[col][row] == q2


    def space_is_open(self, col, row):
        """
        Sanity check to see if a space is within the bounds of the board and blank. Not meant to be called directly if you don't know what 
        you're looking for.
        Parameters:
            col: int, Col value of desired space
            row: int, Row value of desired space
        Returns:
            bool: (Col, Row ranges are valid) AND (space is blank)
        """
        return 0 <= col < self.height and \
               0 <= row < self.width and \
               self.__board_state__[row][col] == Board.BLANK

    def print_board(self, legal_moves=[]):
        """
        Function for printing board state & indicating possible moves for active player.
        Parameters:
            legal_moves: [(int, int)], List of legal moves to indicate when printing board spaces. 
            Each move takes the form of (column, row).
        Returns:
            Str: Visual interpretation of board state & possible moves for active player
        """

        p1_c, p1_r = self.__last_queen_move__[self.__queen_1__]
        p2_c, p2_r = self.__last_queen_move__[self.__queen_2__]
        b = self.__board_state__

        out = '  |'
        for i in range(len(b[0])):
            out += str(i) + ' |'
        out += '\n\r'

        for i in range(len(b)):
            out += str(i) + ' |'
            for j in range(len(b[i])):
                if (i, j) == (p1_c, p1_r):
                    out += self.__queen_symbols__[self.__queen_1__]
                elif (i, j) == (p2_c, p2_r):
                    out += self.__queen_symbols__[self.__queen_2__]
                elif (i, j) in legal_moves or (j, i) in legal_moves:
                    out += 'o '
                if b[i][j] == Board.BLANK:
                    out += '  '
                elif b[i][j] == Board.TRAIL:    
                   out += '- '
                if b[i][j] == Board.BLOCKED:   #changed for skid variant
                    out += '><'
                out += '|'
            if i != len(b) - 1:
                out += '\n\r'

        return out

    def play_isolation(self, time_limit=10000, print_moves=False):
        """
        Method to play out a game of isolation with the agents passed into the Board class.
        Initializes and updates move_history variable, enforces timeouts, and prints the game.
        Parameters:
            time_limit: int, time limit in milliseconds that each player has before they time out.
            print_moves: bool, Should the method print details of the game in real time
        Returns:
            (str, [(int, int)], str): Queen of Winner, Move history, Reason for game over.
            Each move in move history takes the form of (column, row).
        """
        move_history = []

        if platform.system() == 'Windows':
            def curr_time_millis():
                return int(round(time.time() * 1000))
        else:
            def curr_time_millis():
                return 1000 * resource.getrusage(resource.RUSAGE_SELF).ru_utime

        while True:
            game_copy = self.copy()
            move_start = curr_time_millis()

            def time_left():
                # print("Limit: "+str(time_limit) +" - "+str(curr_time_millis()-move_start))
                return time_limit - (curr_time_millis() - move_start)

            if print_moves:
                print("\n", self.__active_players_queen__, " Turn")

            curr_move = self.__active_player__.move(
                game_copy, time_left)  # queen added in return

            # Append new move to game history
            if self.__active_player__ == self.__player_1__:
                move_history.append([curr_move])
            else:
                move_history[-1].append(curr_move)

            # Handle Timeout
            if time_limit and time_left() <= 0:
                return self.__inactive_players_queen__, move_history, \
                       (self.__active_players_queen__ + " timed out.")

            # Safety Check
            legal_moves = self.get_active_moves()
            if curr_move not in legal_moves:
                return self.__inactive_players_queen__, move_history, \
                       (self.__active_players_queen__ + " made an illegal move.")

            # Apply move to game.
            is_over, winner = self.__apply_move__(curr_move)

            if print_moves:
                print("move chosen: ", curr_move)
                print(self.copy().print_board())

            if is_over:
                return self.__inactive_players_queen__, move_history, \
                    self.__active_players_queen__ + " has no legal moves left."
                # if not self.get_active_moves():
                #     return self.__active_players_queen__, move_history, \
                #            (self.__inactive_players_queen__ + " has no legal moves left.")
                # return self.__active_players_queen__, move_history, \
                #        (self.__inactive_players_queen__ + " was forced off the grid.")
       
    def __apply_move_write__(self, move_queen):
        """
        Equivalent to __apply_move__, meant specifically for applying move history to a board 
        for analyzing an already played game.
        Parameters: 
            move_queen: (int, int), Move to apply to board. Takes
            the form of (column, row).
        Returns:
            None
        """

        if move_queen[0] is None or move_queen[1] is None:
            return

        col, row = move_queen
        my_pos = self.__last_queen_move__[self.__active_players_queen__]
        opponent_pos = self.__last_queen_move__[self.__inactive_players_queen__]

        self.__last_queen_move__[self.__active_players_queen__] = move_queen
        self.__board_state__[col][row] = \
            self.__queen_symbols__[self.__active_players_queen__]

        if self.move_is_in_board(my_pos[0], my_pos[1]):
            self.__board_state__[my_pos[0]][my_pos[1]] = Board.BLOCKED

        # Rotate the active player
        tmp = self.__active_player__
        self.__active_player__ = self.__inactive_player__
        self.__inactive_player__ = tmp

        # Rotate the active queen
        tmp = self.__active_players_queen__
        self.__active_players_queen__ = self.__inactive_players_queen__
        self.__inactive_players_queen__ = tmp

        self.move_count = self.move_count + 1


def game_as_text(winner, move_history, termination="", board=Board(1, 2)):
    """
    Function to play out a move history on a new board. Used for analyzing an interesting move history 
    Parameters: 
        move_history: [(int, int)], History of all moves in order of game in question. 
        Each move takes the form of (column, row).
        termination: str, Reason for game over of game in question. Obtained from play_isolation
        board: Board, board that game in question was played on. Used to initialize board copy
    Returns:
        Str: Print output of move_history being played out.
    """
    ans = StringIO()

    board = Board(board.__player_1__, board.__player_2__, board.width, board.height)

    print("Printing the game as text.")

    last_move = (9, 9, 0)

    for i, move in enumerate(move_history):
        if move is None or len(move) == 0:
            continue

        if move[0] != Board.NOT_MOVED and move[0] is not None:
            ans.write(board.print_board())
            board.__apply_move_write__(move[0])
            ans.write("\n\n" + board.__queen_1__ + " moves to (" + str(move[0][0]) + "," + str(move[0][1]) + ")\r\n")

            
        if len(move) > 1 and move[1] != Board.NOT_MOVED and move[0] is not None:
            ans.write(board.print_board())
            board.__apply_move_write__(move[1])
            ans.write("\n\n" + board.__queen_2__ + " moves to (" + str(move[1][0]) + "," + str(move[1][1]) + ")\r\n")

            
        last_move = move

    ans.write("\n" + str(winner) + " has won. Reason: " + str(termination))
    return ans.getvalue()
