# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
from time import time
import random
from copy import deepcopy
from queue import Queue
import math
import pprint

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
        self.first_step = True

    def step(self, chess_board, my_pos, adv_pos, max_step):
        start_time = time()


        state = deepcopy(GameState(chess_board, my_pos, adv_pos, max_step))
        move = None

        moves = state.moves_for_curr_player()
        for n in moves:
            tempState = deepcopy(state)
            tempState.play(n)
            endgame, _, _, winner = tempState.check_endgame()
            if(endgame and winner == 1):
                my_pos, dir = n
                print("attack")
                return n
        
        # Check for winner
        endgame, my_score, adv_score, winner = state.check_endgame()

        if not endgame:
            foo = MCTS(state)
            # if(self.first_step == True):
            #     foo.search(30)
            #     self.first_step = False
            # else:
            foo.search(1.8)

            my_pos, dir = move = foo.best_move()

        state.play(move)

        # arb_move = random.choice(state.moves_for_curr_player())
        # my_pos, dir = arb_move
        # while(not endgame):
        #     moves = state.moves_for_curr_player()
        #     print(moves)
        #     state.play(random.choice(moves))
        #     endgame, my_score, adv_score, winner = state.check_endgame()
        print(time()-start_time)
        return my_pos, dir

class MCTS:
    def __init__(self, state):
        self.root_state = deepcopy(state)
        self.root = Node()
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0

    def heuristic_choice(self, moves, state):
        nonBoarderMoves = []
        for move in moves:
            tempState = deepcopy(state)
            player = tempState.to_play
            tempState.play(move)
            endgame, _, _, winner = tempState.check_endgame()
            if(endgame == True):
                if(winner == player):
                    return move
                else: 
                    moves.remove(move)
            else:
                if(move[0][0] != 0 and move[0][0] != state.size-1 and move[0][1] != 0 and move[0][1] != state.size-1):
                    nonBoarderMoves.append(move)
        if(len(nonBoarderMoves) != 0):
            return random.choice(nonBoarderMoves)
        else:
            return random.choice(moves)
        

    def search(self, time_limit):
        """
        Search and update the tree for a limited amount of time.
        """
        start_time = time()
        num_rollouts = 0

        # While time available. Can simplify given our 2 second limit?
        while time() - start_time < time_limit:
            node, state = self.select_node()
            outcome = self.roll_out(state)
            turn = state.to_play
            self.backup(node, turn, outcome)
            num_rollouts += 1
        
        self.run_time = time() - start_time       # Delete?
        self.node_count = self.tree_size()
        self.num_rollouts = num_rollouts
        print(num_rollouts)

    def select_node(self):
        """
        Select a node in the tree to perform one simulation.
        """
        node = self.root
        state = deepcopy(self.root_state)

        # While we are not inspecting a terminal node.
        while len(node.children) != 0:
            children = node.children.values()
            max_nodes = []
            max_value = max(children, key=lambda n: n.value).value

            for n in children:
                if n.value == max_value:
                    max_nodes.append(n)

            if len(max_nodes) == 1:
                node = max_nodes[0]
            else:
                moves = []
                for n in max_nodes:
                    moves.append(n.move)
                bestMove = self.heuristic_choice(moves, state)
                for n in max_nodes:
                    if n.move == bestMove:
                        node = n
                        break
                # node = self.heuristic_choice(max_nodes, state)   

            state.play(node.move)

            # If child is not explored then select it. Expand children afterwards.
            if node.N == 0:
                return node, state

        # If leaf is reached, then generate its children and return one.
        # If terminal node is reached, return the terminal node.

        if self.expand(node, state):

            childrenValues = list(node.children.values())
            if len(childrenValues) != 0:
                if len(childrenValues) == 1:
                    node = childrenValues[0]
                else:
                    moves = []
                    for child in childrenValues:
                        moves.append(child.move)
                    bestMove = self.heuristic_choice(moves, state)
                    for child in childrenValues:
                        if child.move == bestMove:
                            node = child
                            break
                    # node = random.choice(childrenValues)
                state.play(node.move)
        
        return node, state

    @staticmethod
    def expand(parent, state):
        """
        Generate the children of the passed "parent" node based on the available
        moves in the passed gamestate and add them to the tree.
        """
        children = []

        # If winner has been determined the game is over and expanding is done
        if state.check_endgame()[0]:
            return False

        # Else expand chilrden
        for move in state.moves_for_curr_player():
            children.append(Node(move, parent))
            #pprint.pprint(vars(Node(move, parent)))
        # print(len(children))
        parent.add_children(children)
        return True

    def roll_out(self, state):
        """
        Simulate an entirely random game from the passed state and return the winning player.
        Input: GameState
        Output: Winner of the game
        """
        
        # While winner has not been determined
        while state.check_endgame()[0] == False:
            # get list of moves for current player
            moves = state.moves_for_curr_player()
            if(len(moves) == 0):
                return 0 if state.to_play == 1 else 1
            if len(moves) == 1:
                move = moves[0]
            else:
                move = self.heuristic_choice(moves, state)
            state.play(move)
            # print(state.check_endgame()[1:3])
        return state.check_endgame()[3]

    @staticmethod
    def backup(node, turn, outcome):
        """
        Update node statistics on the path from the passed node to the root
        to reflect the outcome of a randomly simulated playout.
        Input:
            Node
            Turn: winner turn
            Outcome: outcome of rollout
        Output:
            Object:
        """
        
        # Calculate the reward for the player who just played at the node. Not next player to play.
        if outcome == 0.5: reward = 0.5
        else:
            if outcome == turn: reward = 0
            else: reward = 1
        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent
            if outcome == 0.5: reward = 0.5
            else:
                if reward == 1: reward = 0
                else: reward = 1

    def best_move(self) -> tuple:
            """
            Return the best move according to the current tree.
            Returns:
                best move in terms of the most simulations number unless the game is over
            """
            if self.root_state.check_endgame()[0] == True:
                return self.root_state.check_endgame()[0] # return GAME_OVER

            # if there is a node that leads to endgame and we win, pick it
            moves = []
            for n in self.root.children.values():
                print(n.move)
                tempState = deepcopy(self.root_state)
                player = tempState.to_play
                tempState.play(n.move)
                endgame, _, _, winner = tempState.check_endgame()
                if(endgame == True):
                    if(winner == player):
                        print("here")
                        return n.move

            # choose the move of the most simulated node breaking ties randomly
            max_value = max(self.root.children.values(), key=lambda n: n.N).N
            max_nodes = [n for n in self.root.children.values() if n.N == max_value]
            # print(len(max_nodes))
            moves = []
            for node in max_nodes:
                moves.append(node.move)
            bestMove = self.heuristic_choice(moves, self.root_state)
            for node in max_nodes:
                if node.move == bestMove:
                    bestchild = node
                    break
            # bestchild = self.heuristic_choice(max_nodes, self.root_state)

            return bestchild.move

    def move(self, move: tuple) -> None:
        """
        Make the passed move and update the tree appropriately. It is
        designed to let the player choose an action manually (which might
        not be the best action).
        Args:
            move:
        """
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.root_state.play(child.move)
            return

        # if for whatever reason the move is not in the children of
        # the root just throw out the tree and start over
        self.root_state.play(move)
        self.root = Node()

    def set_gamestate(self, state):
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.
        """
        self.root_state = deepcopy(state)
        self.root = Node()

    def statistics(self):
        return self.num_rollouts, self.node_count, self.run_time

    def tree_size(self):
        """
        Count nodes in tree by BFS.
        """
        Q = Queue()
        count = 0
        Q.put(self.root)
        while not Q.empty():
            node = Q.get()
            count += 1
            for child in node.children.values():
                Q.put(child)
        return count

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

    @property
    def value(self, explore = 0.5):
        """
        Calculate the UCT of this node relative to its parent
        Explore parameter: 
            specifices how much the value should favor nodes that have 
            yet to be explored versus nodes that seem to have a high win rate
        """
        if self.N == 0:
            return 0 if explore == 0 else sys.maxsize
        else:
            return self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)

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