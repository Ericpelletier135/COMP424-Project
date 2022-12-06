# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
from time import time
import random
from copy import deepcopy
from gamestate import GameState
from queue import Queue
import math
import pprint


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
            return 0 if explore == 0 else -1
        else:
            return self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)


@register_agent("matts_alt_agent")
class MattsAltAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(MattsAltAgent, self).__init__()
        self.name = "MattsAltAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

    def step(self, chess_board, my_pos, adv_pos, max_step):
        start_time = time()


        state = deepcopy(GameState(chess_board, my_pos, adv_pos, max_step))
        move = None

        
        # Check for winner
        endgame, my_score, adv_score, winner = state.check_endgame()

        if not endgame:
            foo = MCTS(state)
            foo.search(1.99)

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

    def search(self, time_limit) -> None:
        """
        Search and update the tree for a limited amount of time.
        """
        start_time = time()
        num_rollouts = 0

        # While time available. Can simplify given our 2 second limit?
        while time() - start_time < time_limit:
            node, state = self.select_node()
            turn = self.root_state.to_play
            outcome = self.roll_out(state)
            self.backup(node, turn, outcome)
            num_rollouts += 1
        
        self.run_time = time() - start_time       # Delete?
        self.node_count = self.tree_size()
        self.num_rollouts = num_rollouts

    def select_node(self) -> tuple:
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
                node = random.choice(max_nodes)   

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
                    node = random.choice(childrenValues)
                
                state.play(node.move)
        
        return node, state

    @staticmethod
    def expand(parent: Node, state: GameState) -> bool:
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

    @staticmethod
    def roll_out(state: GameState) -> int:
        """
        Simulate an entirely random game from the passed state and return the winning player.
        Input: GameState
        Output: Winner of the game
        """

        # Store list of all possible moves in current state of the game
        moves = state.moves_for_curr_player()
        
        # While winner has not been determined
        while state.check_endgame() == False:
            move = random.choice(moves)
            state.play(move)
            moves.remove(move)

        return state.check_endgame()

    @staticmethod
    def backup(node: Node, turn: int, outcome: int) -> None:
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
        if outcome == turn: reward = 0
        else: reward = 1
        while node is not None:
            node.N += 1
            node.Q += reward
            node = node.parent
            if reward == 1: reward = 0
            else: reward = 1

    def best_move(self) -> tuple:
            """
            Return the best move according to the current tree.
            Returns:
                best move in terms of the most simulations number unless the game is over
            """
            if self.root_state.check_endgame == True:
                return self.root_state.check_endgame # return GAME_OVER

            # choose the move of the most simulated node breaking ties randomly
            max_value = max(self.root.children.values(), key=lambda n: n.N).N
            max_nodes = [n for n in self.root.children.values() if n.N == max_value]
            bestchild = random.choice(max_nodes)

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

    def set_gamestate(self, state: GameState) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.
        """
        self.root_state = deepcopy(state)
        self.root = Node()

    def statistics(self) -> tuple:
        return self.num_rollouts, self.node_count, self.run_time

    def tree_size(self) -> int:
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