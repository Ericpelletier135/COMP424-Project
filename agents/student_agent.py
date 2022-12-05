# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
from time import time
from copy import deepcopy
import math


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))


    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        "dummy text"

        # print(max_step)

        start_time = time()
    
        # moves = self.generate_valid_moves(chess_board, my_pos, adv_pos, max_step)

        # initialNode = Node(moves[0])
        state = deepcopy(GameState(chess_board, my_pos, adv_pos, max_step))
        
        endgame, my_score, adv_score, winner = state.check_endgame()
        while(not endgame):
            moves = state.moves_for_curr_player()
            state.play(moves[0])
            endgame, my_score, adv_score, winner = state.check_endgame()

        print("winner: ", winner)


        # Create board states from moves, (update chess_board true false value at location of move and update my_pos to move)
    
        # print("Time taken: ", time() - start_time)

        # dummy return
        return my_pos, self.dir_map["u"]

class GameState:
    """
    Stores information representing the current state of a game, namely
    the board and the current turn. Also provides functions for playing game.
    """

    def __init__(self, chess_board, my_pos, adv_pos, max_step):
        self.size = len(chess_board[0])
        self.to_play = 1 #set to 1 if its our turn to play, otherwise 0
        self.chess_board = deepcopy(chess_board)
        self.my_pos = my_pos
        self.adv_pos = adv_pos
        self.max_step = max_step
        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

    def play(self, move):
        """
        Play the move for the current player
        """
        if self.to_play == 1:
            self.play_my_move(move)
            self.to_play = 0
        else: 
            self.play_adv_move(move)
            self.to_play = 1

    def play_my_move(self, move):
        """
        Play the move for my player
        """
        pos, dir = move
        my_x, my_y = pos
        self.chess_board[my_x][my_y][dir] = True
        self.my_pos = pos
    
    def play_adv_move(self, move):
        """
        Play the move for my player
        """
        pos, dir = move
        adv_x, adv_y = pos
        self.chess_board[adv_x][adv_y][dir] = True
        self.adv_pos = pos

    def moves_for_curr_player(self):
        """
        Get a list of the valid moves to play
        """
        valid_moves = []
        if self.to_play == 1:
            pos = self.my_pos
            pos_x, pos_y = pos
            opp_pos = self.adv_pos
        else:
            pos = self.adv_pos
            pos_x, pos_y = pos 
            opp_pos = self.my_pos

        for x in range(0, self.max_step+1): # variable length of move
            for y in range(0, self.max_step+1-x):
                for barrier_dir in range(4):
                    negative_x = pos_x-x
                    positive_x = pos_x+x
                    negative_y = pos_y-y
                    positive_y = pos_y+y

                    if(x == 0):
                        if(y == 0):
                            if self.check_valid_step(pos, pos, barrier_dir, opp_pos):
                                valid_moves.append((pos, barrier_dir))
                        else:
                            if(negative_y >= 0):
                                end_pos = (pos_x, negative_y)
                                if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                    valid_moves.append((end_pos, barrier_dir))
                            if(positive_y < self.size):
                                end_pos = (pos_x, positive_y)
                                if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                    valid_moves.append((end_pos, barrier_dir))
                    else:
                        if(negative_x >= 0):
                            if(y == 0):
                                end_pos = (negative_x, pos_y)
                                if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                    valid_moves.append((end_pos, barrier_dir))
                            else:
                                if(negative_y >= 0):
                                    end_pos = (negative_x, negative_y)
                                    if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                        valid_moves.append((end_pos, barrier_dir))
                                if(positive_y < self.size):
                                    end_pos = (negative_x, positive_y)
                                    if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                        valid_moves.append((end_pos, barrier_dir))
                        if(positive_x < self.size):
                            if(y == 0):
                                end_pos = (negative_x, pos_y)
                                if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                    valid_moves.append((end_pos, barrier_dir))
                            else:
                                if(negative_y >= 0):
                                    end_pos = (positive_x, negative_y)
                                    if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                        valid_moves.append((end_pos, barrier_dir))
                                if(positive_y < self.size):
                                    end_pos = (positive_x, positive_y)
                                    if self.check_valid_step(pos, end_pos, barrier_dir, opp_pos):
                                        valid_moves.append((end_pos, barrier_dir))

        return valid_moves

    def check_valid_step(self, start_pos, end_pos, barrier_dir, adv_pos):
        """
        Check if the step the agent takes is valid (reachable and within max steps).

        Parameters
        ----------
        start_pos : tuple
            The start position of the agent.
        end_pos : np.ndarray
            The end position of the agent.
        barrier_dir : int
            The direction of the barrier.
        """
        # Endpoint already has barrier or is boarder
        r, c = end_pos
        if self.chess_board[r][c][barrier_dir]:
            return False
        if (start_pos == end_pos):
            return True

        # BFS
        state_queue = [(start_pos, 0)]
        visited = {tuple(start_pos)}
        is_reached = False
        while state_queue and not is_reached:
            cur_pos, cur_step = state_queue.pop(0)
            r, c = cur_pos
            if cur_step == self.max_step:
                break
            for dir, move in enumerate(self.moves):
                if self.chess_board[r][c][dir]:
                    continue

                move_x, move_y = move
                next_pos = (r+move_x, c+move_y)
                if (next_pos == adv_pos) or tuple(next_pos) in visited:
                    continue
                if (next_pos == end_pos):
                    is_reached = True
                    break

                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        return is_reached

    def check_endgame(self):
        """
        Check if the game ends and compute the current score of the agents.

        Returns
        -------
        is_endgame : bool
            Whether the game ends.
        player_1_score : int
            The score of player 1.
        player_2_score : int
            The score of player 2.
        winner : int
            1 if my_player won, 0 if adv_player won and -1 if tie
        """
        # Union-Find
        father = dict()
        for r in range(self.size):
            for c in range(self.size):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(self.size):
            for c in range(self.size):
                for dir, move in enumerate(
                    self.moves[1:3]
                ):  # Only check down and right
                    if self.chess_board[r, c, dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(self.size):
            for c in range(self.size):
                find((r, c))
        p0_r = find(tuple(self.my_pos))
        p1_r = find(tuple(self.adv_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        winner = None
        if p0_r == p1_r:
            return False, p0_score, p1_score, winner
        if p0_score > p1_score:
            winner = 1
        elif p0_score < p1_score:
            winner = 0
        else:
            winner = -1  # Tie
        return True, p0_score, p1_score, winner

class Node:
    """
    Node for the MCTS. Stores the move applied to reach this node from its parent,
    stats for the associated game position, children, parent and outcome
    (outcome==none unless the position ends the game).
    Args:
        move: potential action in each state
        parent: points to the parent node
        N (int): times this position was visited.
        Q (int): average reward (wins-losses) from this position.
        # Q_RAVE (int): will be explained later.
        # N_RAVE (int): will be explained later.
        children (dict): dictionary of successive nodes.
        outcome (int): If node is a leaf, then outcome indicates
                       the winner, else None.
    """

    def __init__(self, move: tuple = None, parent: object = None):
        """
        Initialize a new node with optional move and parent and initially empty
        children list and rollout statistics and unspecified outcome.
        """
        self.move = move
        self.parent = parent
        self.N = 0 # times this node was visited
        self.Q = 0 # average reward from this node
        self.children = {}
        self.outcome = None # if node is a leaf, then outcome indicates the winner, else None

    def add_children(self, children):
        for child in children:
            self.children[child.move] = child

    def value(self, explore = 0.5):
        """
        Calculate the UCT of this node relative to its parent
        Explore parameter: 
            specifices how much the value should favor nodes that have 
            yet to be explored versus nodes that seem to have a high win rate
        """
        if self.N == 0:
            return 0 if explore == 0 else -1
        else:
            return self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)

    

