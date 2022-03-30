import gym
import random
import requests
import numpy as np
import argparse
import sys
from gym_connect_four import ConnectFourEnv
import math
import copy

env: ConnectFourEnv = gym.make("ConnectFour-v0")

# SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["an3668pa-s"]  # TODO: fill this list with your stil-id's


def call_server(move):
    res = requests.post(SERVER_ADRESS + "move",
                        data={
                            "stil_id": STIL_ID,
                            "move": move,
                            # -1 signals the system to start a new game. any running game is counted as a loss
                            "api_key": API_KEY,
                        })
    # For safety some respose checking is done here
    if res.status_code != 200:
        print("Server gave a bad response, error code={}".format(res.status_code))
        exit()
    if not res.json()['status']:
        print("Server returned a bad status. Return message: ")
        print(res.json()['msg'])
        exit()
    return res


def check_stats():
    res = requests.post(SERVER_ADRESS + "stats",
                        data={
                            "stil_id": STIL_ID,
                            "api_key": API_KEY,
                        })

    stats = res.json()
    return stats


"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""


def opponents_move(env):
    #Changing betweeen players, student move before we return -1.
    env.change_player()
    avmoves = env.available_moves()
    if not avmoves:
        env.change_player()
        return -1

    action = random.choice(list(avmoves))

    state, reward, done, _ = env.step(action)
    if done:
        #rewards the current player
        if reward == 1:
            reward = -1
    env.change_player()
    return state, reward, done


def student_move(board):
   board = np.array(board)
   #Minimax algorithm is specified with arguments and i starting of at the root [0]
   return minimax(board, 5, -math.inf, math.inf, True)[0]


def minimax(board, depth, alpha, beta, maxPlayer):
   """
   Minimax algorithm performs on a board with arguments that specifies depth and alpha-beta pruning.
   Returning the value of the board, or basically the upcomming score after the next move,
   from the maximizing player point of view, or "not max_player" if it is the opponents move
   """
   #Will stop and check method "nbr_in_a_row" if it isn't a winning move or depth 0
   if depth == 0 or winning_move(board, maxPlayer) or winning_move(board, not maxPlayer):
      return nbr_in_a_row(board)
   if maxPlayer:
       #Starts off as the worst possible move (illegal) and score (worst int)
      best_choice = [-2, -math.inf]
      for move in valid_moves(board):
          #Creating a copy of the new board to compare with
         copy_of_board = copy.deepcopy(board)
         play_move(copy_of_board, move, maxPlayer)
         #Will run minimax recursively until there is a winning move or depth=0
         new_choice = minimax(copy_of_board, depth-1, alpha, beta, not maxPlayer)[1]
         #Comparison between last saved score
         if new_choice > best_choice[1]:
            best_choice = [move, new_choice]
         #Breaks loop if alpha-beta pruning shows the sequence is done to save time and data
         alpha = max_value(alpha, best_choice[1])
         if beta <= alpha:
            break
      return best_choice
   else:
      worst_choice = [-2, math.inf]
      for move in valid_moves(board):
         copy_of_board =  copy.deepcopy(board)
         play_move(copy_of_board, move, maxPlayer)
         #Second move in our vector "[1]", opponents move
         new_choice = minimax(copy_of_board, depth-1, alpha, beta, not maxPlayer)[1]
         #Comparison between last saved score
         if new_choice < worst_choice[1]:
            worst_choice = [move, new_choice]
         beta = min_value(beta, worst_choice[1])
         #Breaks loop if alpha-beta pruning shows the sequence is done to save time and data
         if beta <= alpha:
            break
      return worst_choice

def play_move(board, col:int, maxPlayer:bool):
   """
   Makes sure the game follows the right rules. Will put the move in the lowest possible row in the specified column
   """
   for row in range(5, -1, -1):
      if board[row,col] == 0:
         if maxPlayer:
            board[row,col] = 1
            break
         else:
            board[row,col] = -1
            break
   return board

def valid_moves(board):
   """
   Returns valid board locations as a list
   """
   return list((x for x in range(len(board[0])) if valid_move(board, x)))

   """
   Checks if top row in the specified column is empty
   """
def valid_move(board, col):
    return board[0][col] == 0


def evaluate_board(row):
   """
   Takes a set of four cells and finds numbers of cells that is located in a row. Returns the score of the row,
   i.e how many slot the players have in row. Will return a positive score for when the maximizing player
   have two-four in a row, and a negative value if the opponent has 2-4 slots in a row. The opponents numbers
   are bigger for scores up to four in a row, that means that we intend to block instead of pushing for a higher
   sequence of our own score. Except when it means that we get four in row, then it is a winning move
   and should be prioritized.
   """

   max_player_slots = 0
   opponent_slots = 0
   empty_slots = 0
   score = 0

   for slot in row:
      if slot == 1:
         max_player_slots += 1
      elif slot == -1:
         opponent_slots +=1
      else:
         empty_slots += 1

   if max_player_slots == 4:
      score = 100
   elif max_player_slots == 3 and empty_slots == 1:
      score = 12
   elif max_player_slots == 2 and empty_slots == 2:
      score = 1
   elif opponent_slots == 2 and empty_slots == 2:
      score = -3
   elif opponent_slots == 3 and empty_slots == 1:
      score = -13
   elif opponent_slots == 4:
       score = -99

   return score

#compar values, wants maximum
def max_value(value, other):
   if other > value:
      return other
   return value
#compar values, wants minimum
def min_value(value, other):
   if other < value:
      return other
   return value


def nbr_in_a_row(board):
   """
   Analyzes the current position in the "board" then returns value as "in_a_row" depending
   on the state. Returns -1 if it is an illegal move. Check each set, horizontal,
   verical and diagonal, sieves out the non poosible set of 4 by putting in range
   """
   in_a_row = 0

   for row in range(6):
       if board[row,3] == 1:
           in_a_row += 1


   for column in np.flip(np.transpose(board)):
      for y in range(3):
            set_of_cells = [column[y], column[y+1], column[y+2], column[y+3]]
            in_a_row += evaluate_board(set_of_cells)

   for row in board:
      for x in range(4):
            set_of_cells = [row[x], row[x+1], row[x+2], row[x+3]]
            in_a_row += evaluate_board(set_of_cells)

   for y in range(3):
      for x in range(7):
         if x > 2:
            set_of_cells= [board[y, x], board[y+1, x-1], board[y+2, x-2], board[y+3, x-3]]
            in_a_row += evaluate_board(set_of_cells)
         if x < 4:
            set_of_cells= [board[y, x], board[y+1, x+1], board[y+2, x+2], board[y+3, x+3]]
            in_a_row += evaluate_board(set_of_cells)

   return [-1, in_a_row]


def winning_move(board, maxPlayer):
   """
   Analyzing how many slots in a row the players have and if there are a winning move
   (set of three in a row before the move) in the current position.
   Returns true if it exist a winning move else false
   """
   if maxPlayer:
      winningScore = 100
   else:
      winningScore = -99

   # Vertical
   for column in np.flip(np.transpose(board)):
      for y in range(3):
            set_of_cells = [column[y], column[y+1], column[y+2], column[y+3]]
            in_a_row = evaluate_board(set_of_cells)
            if in_a_row == winningScore:
               return True

   # Horizontal
   for row in board:
      for x in range(4):
            set_of_cells = [row[x], row[x+1], row[x+2], row[x+3]]
            in_a_row = evaluate_board(set_of_cells)
            if in_a_row == winningScore:
               return True

   # Diagonal both ways
   for y in range(3):
      for x in range(7):
         if x < 4:
            set_of_cells= [board[y, x], board[y-1, x+1], board[y-2, x+2], board[y-3, x+3]]
            in_a_row += evaluate_board(set_of_cells)
            if in_a_row == winningScore:
               return True
         if x > 2:
            set_of_cells= [board[y, x], board[y-1, x-1], board[y-2, x-2], board[y-3, x-3]]
            in_a_row += evaluate_board(set_of_cells)
            if in_a_row == winningScore:
               return True
   return False

def play_game(vs_server=False):
    """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

    # default state
    state = np.zeros((6, 7), dtype=int)

    # setup new game
    if vs_server:
        # Start a new game
        res = call_server(-1)  # -1 signals the system to start a new game. any running game is counted as a loss

        # This should tell you if you or the bot starts
        print(res.json()['msg'])
        botmove = res.json()['botmove']
        state = np.array(res.json()['state'])
    else:
        # reset game to starting state
        env.reset(board=None)
        # determine first player
        student_gets_move = random.choice([True, False])
        if student_gets_move:
            print('You start!')
            print()
        else:
            print('Bot starts!')
            print()

    # Print current gamestate
    print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
    print(state)
    print()

    done = False
    while not done:
        # Select your move
        stmove = student_move(state)  # TODO: change input here

        # make both student and bot/server moves
        if vs_server:
            # Send your move to server and get response
            res = call_server(stmove)
            print(res.json()['msg'])

            # Extract response values
            result = res.json()['result']
            botmove = res.json()['botmove']
            state = np.array(res.json()['state'])
        else:
            if student_gets_move:
                # Execute your move
                avmoves = env.available_moves()
                if stmove not in avmoves:
                    print("You tied to make an illegal move! You have lost the game.")
                    break
                state, result, done, _ = env.step(stmove)

            student_gets_move = True  # student only skips move first turn if bot starts

            # print or render state here if you like

            # select and make a move for the opponent, returned reward from students view
            if not done:
                state, result, done = opponents_move(env)

        # Check if the game is over
        if result != 0:
            done = True
            if not vs_server:
                print("Game over. ", end="")
            if result == 1:
                print("You won!")
            elif result == 0.5:
                print("It's a draw!")
            elif result == -1:
                print("You lost!")
            elif result == -10:
                print("You made an illegal move and have lost!")
            else:
                print("Unexpected result result={}".format(result))
            if not vs_server:
                print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
        else:
            print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

        # Print current gamestate
        print(state)
        print()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--local", help="Play locally", action="store_true")
    group.add_argument("-o", "--online", help="Play online vs server", action="store_true")
    parser.add_argument("-s", "--stats", help="Show your current online stats", action="store_true")
    args = parser.parse_args()


    # Print usage info if no arguments are given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.local:
        play_game(vs_server=False)
    elif args.online:
        play_game(vs_server=True)

    if args.stats:
        stats = check_stats()
        print(stats)

    # TODO: Run program with "--online" when you are ready to play against the server
    # the results of your games there will be logged
    # you can check your stats bu running the program with "--stats"


if __name__ == "__main__":
    main()
