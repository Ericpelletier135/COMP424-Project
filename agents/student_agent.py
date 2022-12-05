# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys


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

    def valid_moves(self, chess_board, my_pos, adv_pos):
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        max_size = len(chess_board[0])
        valid_moves = []
        for mov_dir in range(4): #each direaction
            my_x, my_y = my_pos
            if(not chess_board[my_x][my_y][mov_dir]):
                move_x, move_y = moves[dir]
                future_x = my_x+move_x
                future_y = my_y+move_y
                if((future_x, future_y) != adv_pos):
                    valid_moves.append((future_x, future_y))

        
        return valid_moves

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
        
        # #putting wall without moving
        # for mov_dir in range(4): #each direaction
        #     my_x, my_y = my_pos
        #     if(not chess_board[my_x][my_y][mov_dir]):
        #         moves.append((my_pos, mov_dir))

        # initial_moves = self.valid_moves(chess_board, my_pos, adv_pos)

        # for move in initial_moves:
        #     for i in range(max_step):
        #         my_x, my_y = move
        #         for mov_dir in range(4): #each direaction
        #             if(not chess_board[my_x][my_y][mov_dir]):
        #                 move_to_add = ((my_x, my_y), mov_dir)
        #                 if(move_to_add not in moves):
        #                     moves.append(move_to_add)
        #     next_move = self.valid_moves(chess_board, next_move, adv_pos)



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




        # for x in range(0, max_step+1): # variable length of move
            
        #     for y in range(0, max_step+1-x):
        #         for dir in range(4):
        #             if(x == 0):
        #                 if(y == 0):
        #                     if(not chess_board[my_x][my_y][dir]):
        #                             moves.append(((my_x, my_y), dir))
        #                 else:
        #                     negative_y = my_y-y
        #                     positive_y = my_y+y
        #                     if(negative_y >= 0):    
        #                         if((not chess_board[my_x][negative_y][dir]) and (my_x, negative_y) != adv_pos):
        #                             moves.append(((my_x, negative_y), dir))
        #                         if(positive_y < max_size):    
        #                             if((not chess_board[my_x][positive_y][dir]) and (my_x, positive_y) != adv_pos):
        #                                 moves.append(((my_x, positive_y), dir))
        #             else:
        #                 negative_x = my_x-x
        #                 positive_x = my_x+x
        #                 if(negative_x >= 0):
        #                     if(y == 0):
        #                         if((not chess_board[negative_x][my_y][dir]) and (negative_x, my_y) != adv_pos):
        #                             moves.append(((negative_x, my_y), dir))
        #                     else:
        #                         negative_y = my_y-y
        #                         positive_y = my_y+y
        #                         if(negative_y >= 0):    
        #                             if((not chess_board[negative_x][negative_y][dir]) and (negative_x, negative_y) != adv_pos):
        #                                 moves.append(((negative_x, negative_y), dir))
        #                             if(positive_y < max_size):    
        #                                 if((not chess_board[negative_x][positive_y][dir]) and (negative_x, positive_y) != adv_pos):
        #                                     moves.append(((negative_x, positive_y), dir))
        #                 if(positive_x < max_size):
        #                     if(y == 0):
        #                         if((not chess_board[negative_x][my_y][dir]) and (negative_x, my_y) != adv_pos):
        #                             moves.append(((negative_x, my_y), dir))
        #                     else:
        #                         if(negative_y >= 0):    
        #                             if((not chess_board[positive_x][negative_y][dir]) and (positive_x, negative_y) != adv_pos):
        #                                 moves.append(((positive_x, negative_y), dir))
        #                         if(positive_y < max_size):    
        #                             if((not chess_board[positive_x][positive_y][dir]) and (positive_x, positive_y) != adv_pos):
        #                                 moves.append(((positive_x, positive_y), dir))
                        

        return valid_moves


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

        moves = self.generate_valid_moves(chess_board, my_pos, adv_pos, max_step)

        # dummy return
        return moves


