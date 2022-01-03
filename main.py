import sys
import random
import argparse
from operator import sub
from copy import deepcopy

cardinalToPos = dict({
    "n": (-1,0), 
    "ne": (-1,1), 
    "e": (0,1), 
    "se": (1,1), 
    "s": (1,0), 
    "sw": (1,-1), 
    "w": (0,-1), 
    "nw": (-1,-1)})

posToCardinal  = {v: k for k, v in cardinalToPos.items()}

BLANK = " "
MIDDLE = (2,2)

class Slot():
    def __init__(self, position):
        self.position = position
        self.curr_worker = BLANK
        self.curr_height = 0
        self.possibleMoves = self.boundaryCheck()

    def __repr__(self):
        rep = f"{self.curr_height}{self.curr_worker}"
        return rep

    def boundaryCheck(self):
        possible_moves = []
        all_moves = [(1, 0), (1, 1), (1, -1), (0, -1), (0, 1), (-1, 0), (-1, -1), (-1, 1)]
        for move in all_moves:
            pos = tuple(map(sum,zip(self.position, move)))
            if pos[0] < 0 or pos[0] > 4 or pos[1] < 0 or pos[1] > 4:
                continue
            else:
                possible_moves.append(pos)

        return possible_moves

class Player():
    def __init__(self, player_type, score_display):
        self.player_type = player_type
        self.score_display = score_display
        self.score = None

class WhitePlayer(Player):
    def __init__(self, player_type, score_display):
        super().__init__(player_type=player_type, score_display=score_display)
        self.workers = ["A", "B"]
        self.worker_pos = {"A": [3, 1], "B": [1, 3]}
        self.color = "white"

    def __repr__(self):
        if self.score_display == "off":
            return f"white (AB)"
        else:
            return f"white (AB), {self.score}"

class BluePlayer(Player):
    def __init__(self, player_type, score_display):
        super().__init__(player_type=player_type, score_display=score_display)
        self.workers = ["Y", "Z"]
        self.worker_pos = {"Y": [1, 1], "Z": [3, 3]}
        self.color = "blue"

    def __repr__(self):
        if self.score_display == "off":
            return f"blue (YZ)"
        else:
            return f"blue (YZ), {self.score}"

        
class Santorini():
    def __init__(self, white, blue, undo_redo, score_display):
        self.board = []
        self.white = white
        self.blue = blue
        self.all_workers = ["A", "B", "Y", "Z"]
        self.turn_num = 1
        self.directions = ["n", "ne", "e", "se", "s", "sw", "w", "nw",]
        self.undo_redo = undo_redo
        self.score_display = score_display
        self.win_state = False
        self.win_color = None
        self.undo_redo_options = ["undo", "redo", "next"]

    # fill up the board with empty slots
    def set_up_board(self):
        for i in range(5):
            row = []
            for j in range(5):
                new_slot = Slot(position = (i, j))
                row.append(new_slot)
            self.board.append(row)

        # add workers to their starting positions
        self.board[1][1].curr_worker = "Y"
        self.board[1][3].curr_worker = "B"
        self.board[3][1].curr_worker = "A"
        self.board[3][3].curr_worker = "Z"

    # print the string representation of the board
    def display_board(self):
        barrier = "+--+--+--+--+--+\n|"
        final_barrier = "+--+--+--+--+--+"
        for i in range(5):
            print(barrier, end = "")
            for j in range(5):
                print(f"{repr(self.board[i][j])}|", end = "")
            print('\n', end = "")
        print(final_barrier)

    def valid_move(self, player, worker, build = False):
        """ Returns true if it is valid. Check if the posistion exists, If there is another
            player there, and if the height is less than 1 greater than it.  
            Args: 
                player (Player): The player trying to move.
                direction (string): The move it is trying to make. It is a direction ie: "n", "ne" 
            Return: 
                (tuple) : The next posistion if valid None if not valid.
        """
        valid_moves = []
        possible_moves = self.board[player.worker_pos[worker][0]][player.worker_pos[worker][1]].possibleMoves

        for move in possible_moves:
            if self.board[move[0]][move[1]].curr_worker != BLANK:
                continue
            elif self.board[player.worker_pos[worker][0]][player.worker_pos[worker][1]].curr_height + 1 < self.board[move[0]][move[1]].curr_height and build == False:
                continue
            elif build == True and self.board[move[0]][move[1]].curr_height == 4 :
                continue
            else: 
                valid_moves.append(move)
        
        return valid_moves


    def move_worker(self, player, worker, position):
        worker_pos = player.worker_pos[worker]
        self.board[worker_pos[0]][worker_pos[1]].curr_worker = BLANK
        self.board[position[0]][position[1]].curr_worker = worker
        player.worker_pos[worker] = position

    def game_over(self, player):
        player_workers = player.workers
        pos1 = player.worker_pos[player_workers[0]]
        pos2 = player.worker_pos[player_workers[1]]
        if self.board[pos1[0]][pos1[1]].curr_height == 3 or self.board[pos2[0]][pos2[1]].curr_height == 3:
            return True
        else:
            return False


    def no_possible_moves(self, player):
        player_workers = player.workers
        pos1 = player.worker_pos[player_workers[0]]
        pos2 = player.worker_pos[player_workers[1]]
        valid_moves = self.valid_move(player,player.workers[0])
        valid_moves.extend(self.valid_move(player,player.workers[1]))
        
        if len(valid_moves) == 0:
            self.win_state = True
            if player.color == "white":
                self.win_color = "blue"
            elif player.color == "blue":
                self.win_color = "white"

    def current_score(self, player, opponent):
        worker1 = player.worker_pos[player.workers[0]]
        worker2 = player.worker_pos[player.workers[1]]
        opponent1 = opponent.worker_pos[opponent.workers[0]]
        opponent2 = opponent.worker_pos[opponent.workers[1]]

        height = self.board[worker1[0]][worker1[1]].curr_height + self.board[worker2[0]][worker2[1]].curr_height
        center_score = ((2 - self.distance_formula(worker1, MIDDLE)) + (2 - self.distance_formula(worker2, MIDDLE)))
        moving_distance_score = min(self.distance_formula(worker1, opponent1), self.distance_formula(worker2, opponent1))
        static_distance_score = min(self.distance_formula(worker1, opponent2), self.distance_formula(worker2, opponent2))
        distance_score = 8 - (moving_distance_score + static_distance_score)

        player.score = (height, center_score, distance_score)
        return player.score

    def turn(self, player):
        self.no_possible_moves(player)
        if self.win_state:
            print(f"Turn: {self.turn_num}, {repr(player)}")
            print(f"{self.win_color} has won")
            sys.exit()
        print(f"Turn: {self.turn_num}, {repr(player)}")
        worker = direction = build = None
        undo_redo_input = None

        if self.undo_redo == "on": 
            while undo_redo_input not in self.undo_redo_options:
                undo_redo_input = input("undo, redo, or next\n")
                if undo_redo_input not in self.undo_redo_options:
                    undo_redo_input = None
                elif undo_redo_input == "next":
                    undo_redo_input == None
                    break
                else:
                    return undo_redo_input
                    break
            
        while worker not in self.all_workers:
            worker = input("Select a worker to move\n")
            worker = worker.upper()
            if worker not in self.all_workers:
                print("Not a valid worker")
            elif worker not in player.workers: 
                print("That is not your worker")
                worker = None

        while direction not in self.directions:
            direction = input("Select a direction to move (n, ne, e, se, s, sw, w, nw)\n")
            if direction not in self.directions:
                print("Not a valid direction")
                continue

            valid_moves = self.valid_move(player, worker)
            movement = cardinalToPos[direction]
            nextPosition = tuple(map(sum,zip(player.worker_pos[worker], movement)))
            if nextPosition in valid_moves:
                self.move_worker(player, worker, nextPosition)
            else:
                print(f"Cannot move {direction}")
                direction = None
                continue
                
        while build not in self.directions:
            build = input("Select a direction to build (n, ne, e, se, s, sw, w, nw)\n")
            if build not in self.directions:
                print("Not a valid direction")
                continue

            valid_moves = self.valid_move(player, worker, build = True)
            movement = cardinalToPos[build]
            nextPosition = tuple(map(sum,zip(player.worker_pos[worker], movement)))
            if nextPosition in valid_moves:
                self.board[nextPosition[0]][nextPosition[1]].curr_height += 1
            else:
                print(f"Cannot build {build}")
                build = None
                continue
            
        self.turn_num += 1
        self.display_board()
        if self.game_over(player):
            self.win_state = True
            self.win_color = player.color

    def determine_direction(self, pos_before, pos_after):
        direction = tuple(map(sub, pos_after, pos_before))
        return posToCardinal[direction]

    def random_turn(self, player):
        self.no_possible_moves(player)
        if self.win_state:
            print(f"Turn: {self.turn_num}, {repr(player)}")
            print(f"{self.win_color} has won")
            sys.exit()
        print(f"Turn: {self.turn_num}, {repr(player)}")

        undo_redo_input = None
        if self.undo_redo == "on": 
            while undo_redo_input not in self.undo_redo_options:
                undo_redo_input = input("undo, redo, or next\n")
                if undo_redo_input not in self.undo_redo_options:
                    undo_redo_input = None
                elif undo_redo_input == "next":
                    undo_redo_input == None
                    break
                else:
                    return undo_redo_input
                    break

        worker1 = player.workers[0]
        worker2 = player.workers[1]
        worker1_moves = self.valid_move(player, worker1)
        worker2_moves = self.valid_move(player, worker2)

        move_mappings = {
            worker1: worker1_moves,
            worker2: worker2_moves
        }

        if (len(worker1_moves) > 0) and (len(worker2_moves) > 0):
            worker = random.choice([worker1, worker2])
            move = random.choice(move_mappings[worker])
            
        elif len(worker1_moves) > 0:
            worker = worker1
            move = random.choice(move_mappings[worker])
        else:
            worker = worker2
            move = random.choice(move_mappings[worker])
        
        pos_before = (player.worker_pos[worker][0], player.worker_pos[worker][1])
        self.move_worker(player, worker, move)

        valid_builds = self.valid_move(player, worker, build = True)
        build = random.choice(valid_builds)
        self.board[build[0]][build[1]].curr_height += 1
        print(f"{worker},{(self.determine_direction(pos_before, move))},{self.determine_direction(move, build)}")

        self.turn_num += 1
        self.display_board()
        if self.game_over(player):
            self.win_state = True
            self.win_color = player.color
        
    def distance_formula(self, pos1, pos2):
        distance = tuple(map(sub, pos1, pos2))
        return max(abs(distance[0]), abs(distance[1]))

    def heuristic_turn(self, player, opponent):
        self.no_possible_moves(player)
        if self.win_state:
            print(f"Turn: {self.turn_num}, {repr(player)}")
            print(f"{self.win_color} has won")
            sys.exit()
        print(f"Turn: {self.turn_num}, {repr(player)}")

        undo_redo_input = None
        if self.undo_redo == "on": 
            while undo_redo_input not in self.undo_redo_options:
                undo_redo_input = input("undo, redo, or next\n")
                if undo_redo_input not in self.undo_redo_options:
                    undo_redo_input = None
                elif undo_redo_input == "next":
                    undo_redo_input == None
                    break
                else:
                    return undo_redo_input
                    break
        
        c1 = 3
        c2 = 2
        c3 = 1

        best = 0
        ties = []

        all_valid_moves = []
        worker1_moves = self.valid_move(player, player.workers[0])
        worker2_moves = self.valid_move(player, player.workers[1])
        for move in worker1_moves:
            all_valid_moves.append((player.workers[0], player.workers[1], move))
        for move in worker2_moves:
            all_valid_moves.append((player.workers[1], player.workers[0], move))

        for move in all_valid_moves:
            moving_height = self.board[move[2][0]][move[2][1]].curr_height
            static_height = self.board[player.worker_pos[move[1]][0]][player.worker_pos[move[1]][1]].curr_height
            height_score = moving_height + static_height
            center_score = ((2 - self.distance_formula(move[2], MIDDLE)) + (2 - self.distance_formula(player.worker_pos[move[1]], MIDDLE)))
            moving_distance_score = min(self.distance_formula(move[2], opponent.worker_pos[opponent.workers[0]]), self.distance_formula(player.worker_pos[move[1]], opponent.worker_pos[opponent.workers[0]]))
            static_distance_score = min(self.distance_formula(player.worker_pos[move[1]], opponent.worker_pos[opponent.workers[1]]), self.distance_formula(player.worker_pos[move[1]], opponent.worker_pos[opponent.workers[1]]))
            distance_score = 8 - (moving_distance_score + static_distance_score)

            if moving_height == 3:
                move_score = float('inf')
            else:
                move_score = c1 * height_score + c2 * center_score + c3 * distance_score

            if move_score >= best:
                if move_score == best:
                    ties.append(move)
                else:
                    ties = [move]
                    best = move_score
        
        best_score = random.choice(ties)
        pos_before = (player.worker_pos[best_score[0]][0], player.worker_pos[best_score[0]][1])
        self.move_worker(player, best_score[0], best_score[2])

        valid_builds = self.valid_move(player, best_score[0], build = True)
        build = random.choice(valid_builds)
        self.board[build[0]][build[1]].curr_height += 1
        print(f"{best_score[0]},{(self.determine_direction(pos_before, best_score[2]))},{self.determine_direction(best_score[2], build)}")

        self.turn_num += 1
        self.display_board()
        if self.game_over(player):
            self.win_state = True
            self.win_color = player.color


    def run(self):
        self.set_up_board()
        self.display_board()
        self.play()


class Environment():
    def __init__(self, white_player_type, blue_player_type, undo_redo, score_display):
        self.white = WhitePlayer(white_player_type, score_display = score_display)
        self.blue = BluePlayer(blue_player_type, score_display = score_display)
        self.game = Santorini(self.white, self.blue, undo_redo = undo_redo, score_display = score_display)
        self.history_index = 0
        self.history = []
        self.undo_redo_input = None
    
    def keep_history(self):
        self.history.append(deepcopy(self.game))
    
    def undo(self):
        if self.history_index > 0:
            self.game = deepcopy(self.history[self.history_index - 2])
            self.white = deepcopy(self.game.white)
            self.blue = deepcopy(self.game.blue)
        self.history_index -= 2
        self.run()
    
    def redo(self):
        if self.history_index < len(self.history):
            self.game = deepcopy(self.history[self.history_index])
            self.white = deepcopy(self.game.white)
            self.blue = deepcopy(self.game.blue)
            self.run()
        else:
            self.history_index -= 1
            self.run()
    
    def next(self):
        self.history = self.history[:self.history_index+1]

    def play(self):
        while True:
            self.history_index += 1
            if self.game.turn_num % 2 == 1:
                if self.game.white.player_type == "human":
                    self.game.current_score(self.white, self.blue)
                    undo_redo = self.game.turn(self.white)
                    if undo_redo == "undo" or undo_redo == "redo":
                        return undo_redo
                    else:
                        self.keep_history()
                        self.next()
                elif self.game.white.player_type == "random":
                    self.game.current_score(self.white, self.blue)
                    undo_redo = self.game.random_turn(self.white)
                    if undo_redo == "undo" or undo_redo == "redo":
                        return undo_redo
                    else:
                        self.keep_history()
                        self.next()
                else:
                    self.game.current_score(self.white, self.blue)
                    undo_redo = self.game.heuristic_turn(self.white, self.blue)
                    if undo_redo == "undo" or undo_redo == "redo":
                        return undo_redo
                    else:
                        self.keep_history()
                        self.next()
            else: 
                if self.game.blue.player_type == "human":
                    self.game.current_score(self.blue, self.white)
                    undo_redo = self.game.turn(self.blue)
                    if undo_redo == "undo" or undo_redo == "redo":
                        return undo_redo
                    else:
                        self.keep_history()
                        self.next()
                elif self.game.blue.player_type == "random":
                    self.game.current_score(self.blue, self.white)
                    undo_redo = self.game.random_turn(self.blue)
                    if undo_redo == "undo" or undo_redo == "redo":
                        return undo_redo
                    else:
                        self.keep_history()
                        self.next()
                else:
                    self.game.current_score(self.blue, self.white)
                    undo_redo = self.game.heuristic_turn(self.blue, self.white)
                    if undo_redo == "undo" or undo_redo == "redo":
                        return undo_redo
                    else:
                        self.keep_history()
                        self.next()
    
    def run(self):
        self.game.display_board()
        self.undo_redo_input = self.play()
        if self.undo_redo_input == "undo":
            self.undo()
        else:
            self.redo()

    def boot_up(self):
        self.game.set_up_board()
        self.keep_history()
        self.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process arguments for Santorini', prog = 'main.py', usage='%(prog)s [white player type] [blue player type] [enable undo/redo] [enable score display]')
    parser.add_argument('white_player_type', nargs = '?', type=str, default = "human", help='Player type for White player ("human", "random", or "heuristic",',choices = ["human", "heuristic", "random"])
    parser.add_argument('blue_player_type', nargs = '?', type = str, default= "human", help='Player type for Blue player ("human", "random", or "heuristic",', choices = ["human", "heuristic", "random"])
    parser.add_argument('enable_undo_redo', nargs = '?', type = str, default= "off", help='enable undo/redo ("on" or "off"', choices = ["off", "on"])
    parser.add_argument('enable_score_display', nargs = '?', type = str, default= "off", help='enable score display ("on" or "off"', choices = ["off", "on"])
    args = parser.parse_args()

    env = Environment(args.white_player_type, args.blue_player_type, args.enable_undo_redo, args.enable_score_display)
    env.boot_up()