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
        self.MCST = None
        self.autoplay = True

    def step(self, chess_board, my_pos, adv_pos, max_step):
        start_time = time()

        if(self.first_step):
            self.MCST = MCTS(deepcopy(GameState(chess_board, my_pos, adv_pos, max_step)))
            state = self.MCST.root_state
            move = None

            #check if we can end the game
            moves = state.moves_for_curr_player()
            for n in moves:
                tempState = deepcopy(state)
                tempState.play(n)
                endgame, _, _, winner = tempState.check_endgame()
                if(endgame and winner == 1):
                    my_pos, dir = n
                    return n

            self.MCST.search(20.9)
            my_pos, dir = move = self.MCST.best_move()
            state.play(move)
            self.first_step = False
        else:
            new_dir = None
            for i in range(4):
                if(self.MCST.root_state.chess_board[adv_pos[0]][adv_pos[1]][i] != chess_board[adv_pos[0]][adv_pos[1]][i]):
                    new_dir = i
            
            # play the last players move
            opp_move = (adv_pos, new_dir)
            self.MCST.move(opp_move)

            #check if we can end the game
            moves = self.MCST.root_state.moves_for_curr_player()
            for n in moves:
                tempState = deepcopy(self.MCST.root_state)
                tempState.play(n)
                endgame, _, _, winner = tempState.check_endgame()
                if(endgame and winner == 1):
                    my_pos, dir = n
                    return n

            self.MCST.search(1)
            my_pos, dir = move = self.MCST.best_move()
            self.MCST.move(move)


        
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
        decentMoves = []
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
                numWalls = sum(bool(x) for x in tempState.chess_board[move[0][0]][move[0][1]])
                if(numWalls < 3):
                    decentMoves.append(move)
                if(move[0][0] != 0 and move[0][0] != state.size-1 and move[0][1] != 0 and move[0][1] != state.size-1):
                    nonBoarderMoves.append(move)
        if(len(decentMoves) != 0):
            return random.choice(decentMoves)    
        elif(len(nonBoarderMoves) != 0):
            return random.choice(nonBoarderMoves)
        else:
            if(len(moves) == 1):
                return moves[0]
            else:
                return random.choice(moves)
        

    def search(self, time_limit):
        start_time = time()
        num_rollouts = 0

        # While time available. Can simplify given our 2 second limit?
        while time() - start_time < time_limit:
            node, state = self.select_node()
            if(time() - start_time > time_limit): break
            outcome = self.roll_out(state)
            if(time() - start_time > time_limit): break
            turn = state.to_play
            self.backup(node, turn, outcome)
            num_rollouts += 1
        
        self.run_time = time() - start_time       # Delete?
        self.num_rollouts = num_rollouts

    def select_node(self):
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

            state.play(node.move)

            # If child is not explored then select it
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

                state.play(node.move)
        
        return node, state

    def expand(self, parent, state):
        children = []

        # check if the game is over
        if state.check_endgame()[0]:
            return False

        # Else expand chilrden
        for move in state.moves_for_curr_player():
            children.append(Node(move, parent))
        parent.add_children(children)
        return True

    def roll_out(self, state):        
        # While game is not finished
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

        return state.check_endgame()[3]


    def backup(self, node, turn, outcome):

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

    def best_move(self):
        if self.root_state.check_endgame()[0] == True:
            return self.root_state.check_endgame()[0] # return GAME_OVER

        # choose the move of the most simulated node 
        max_value = max(self.root.children.values(), key=lambda n: n.N).N
        max_nodes = [n for n in self.root.children.values() if n.N == max_value]

        moves = []
        for node in max_nodes:
            moves.append(node.move)
        bestMove = self.heuristic_choice(moves, self.root_state)
        for node in max_nodes:
            if node.move == bestMove:
                bestchild = node
                break
        # bestchild = self.heuristic_choice(max_nodes, self.root_state)
        
        self.root = bestchild

        return bestchild.move


    def move(self, move):
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


class Node:

    def __init__(self, move: tuple = None, parent: object = None):
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
        # calculate UCT of node relative to parent
        if self.N == 0:
            return 0 if explore == 0 else sys.maxsize
        else:
            return self.Q / self.N + explore * math.sqrt(2 * math.log(self.parent.N) / self.N)

class GameState:

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