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

    def check_valid_step(self, start_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
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
        if chess_board[r][c][barrier_dir]:
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
            if cur_step == max_step:
                break
            for dir, move in enumerate(self.moves):
                if chess_board[r][c][dir]:
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

    # Helper function to generate all valid moves from current position as a tuple ((x, y), dir)
    def generate_valid_moves(self, chess_board, my_pos, adv_pos, max_step):
        valid_moves = []
        my_x, my_y = my_pos
        max_size = len(chess_board[0])

        for x in range(0, max_step+1): # variable length of move
            for y in range(0, max_step+1-x):
                for barrier_dir in range(4):
                    negative_x = my_x-x
                    positive_x = my_x+x
                    negative_y = my_y-y
                    positive_y = my_y+y

                    if(x == 0):
                        if(y == 0):
                            if self.check_valid_step(my_pos, my_pos, barrier_dir, chess_board, adv_pos, max_step):
                                valid_moves.append((my_pos, barrier_dir))
                        else:
                            if(negative_y >= 0):
                                end_pos = (my_x, negative_y)
                                if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                    valid_moves.append((end_pos, barrier_dir))
                            if(positive_y < max_size):
                                end_pos = (my_x, positive_y)
                                if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                    valid_moves.append((end_pos, barrier_dir))
                    else:
                        if(negative_x >= 0):
                            if(y == 0):
                                end_pos = (negative_x, my_y)
                                if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                    valid_moves.append((end_pos, barrier_dir))
                            else:
                                if(negative_y >= 0):
                                    end_pos = (negative_x, negative_y)
                                    if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                        valid_moves.append((end_pos, barrier_dir))
                                if(positive_y < max_size):
                                    end_pos = (negative_x, positive_y)
                                    if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                        valid_moves.append((end_pos, barrier_dir))
                        if(positive_x < max_size):
                            if(y == 0):
                                end_pos = (negative_x, my_y)
                                if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                    valid_moves.append((end_pos, barrier_dir))
                            else:
                                if(negative_y >= 0):
                                    end_pos = (positive_x, negative_y)
                                    if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                        valid_moves.append((end_pos, barrier_dir))
                                if(positive_y < max_size):
                                    end_pos = (positive_x, positive_y)
                                    if self.check_valid_step(my_pos, end_pos, barrier_dir, chess_board, adv_pos, max_step):
                                        valid_moves.append((end_pos, barrier_dir))

        return valid_moves

    # def traverse(self, node):


    # def rollout(self, node):

    # def backpropagate(self, node):

    # def best_child(self, node):

    # def monte_carlo_tree_search(self, root, start_time):
    #     while(start_time-time() < 2):
    #         leaf = self.traverse(root)

        

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
    
        moves = self.generate_valid_moves(chess_board, my_pos, adv_pos, max_step)

        initialNode = Node(moves[0])
        

        # Create board states from moves, (update chess_board true false value at location of move and update my_pos to move)
    
        # print("Time taken: ", time() - start_time)

        # dummy return
        return moves[0]


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

    

