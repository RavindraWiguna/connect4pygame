import pygame
from random import randint, choice
from collections import Counter
import numpy as np

# Initialize the pygame
pygame.init()

# Contain the reward, game_over, and score of the game, and just_eat_food
class GameInformation:
    def __init__(self, isWin, winner, isDraw) -> None:
        self.isWin = isWin
        self.winner = winner
        self.isDraw = isDraw

class Game:
    SCORE_FONT = pygame.font.SysFont('comicsans', 50)
    P2_COLOR = (200, 200, 0)
    P1_COLOR = (200, 0, 0)
    EMPTY_COLOR = (0, 0, 100)
    BG = (20, 20, 200)
    COLOR_DICT = {-1: P2_COLOR, 0:EMPTY_COLOR, 1:P1_COLOR}
    DISK_DICT ={-1: "R", 1:"Y"}
    FILL = (1, -1)
    TRANSFORM_1D = [[0,1,2,3,4,5,6],
                    [7,8,9,10,11,12,13],
                    [14,15,16,17,18,19,20],
                    [21,22,23,24,25,26,27],
                    [28,29,30,31,32,33,34],
                    [35,36,37,38,39,40,41]]
    

    def __init__(self, window, width, height, block_size) -> None:
        self.window = window
        self.width = width
        self.height = height
        self.block_size = block_size
        self.half_size = self.block_size//2
        self.total_col = 7
        self.total_row = 6
        self.total_tiles = self.total_col * self.total_row
        if(self.width < self.total_col*self.block_size or self.height < self.total_row*self.block_size):
            raise ValueError(f'{block_size} is too big for ({width} x {height})')
        
        # ith turn of this game (even = 1st player, odd = 2nd player)
        self.turn = 0
        # base for each col for easier filling
        self.col_base = np.array([5]*self.total_col)
        # total disk in each column
        # self.col_fill = np.array([0]*self.total_col)
        # history of move
        self.history_move = []
        # connect four board (p1 prespective)
        '''
        0 = empty
        1 = current turn player Disk
        -1 = next turn player disk
        default is player 1 prespective
        '''
        self.board = np.array([0]*self.total_col*self.total_row, np.int8)

    def load_history(self, historyMove):
        # this function is used to change the board according to history
        # print("loading history")
        for move in historyMove:
            move = int(move)
            self.move(move)
        # print("successfully loaded")

    def get_p2_pov(self):
        return self.board*-1
    
    def check_valid_move(self, col):
        # if(col >= self.total_col):
            # raise ValueError(f"Argument for col:={col} exceed total column:={self.total_col}")
        
        if(self.col_base[col] < 0):
            # print(f"This col: {col} is full")
            return 0
        return 1

    def get_available_move(self):
        avm = []
        for i, colbase in enumerate(self.col_base):
            if(colbase > -1):
                avm.append(i)
        # print(len(avm))
        return avm

    def move(self, col):
        isValid = self.check_valid_move(col)
        if(not isValid):
            return 0

        fill_id = col + self.col_base[col]*7
        # fill the board
        self.board[fill_id] = self.FILL[self.turn&1]
        # update the base
        self.col_base[col]-=1
        # update the fill
        # self.col_fill[col]+=1
        # update history move
        self.history_move.append(str(col))
        # update the turn
        self.turn +=1
        return 1
    
    def get_history_move_str(self):
        return ''.join(self.history_move)

    def check_horizontal_win(self, id):
        if(id%7 > 3):
            # can not go horizontally 4 times
            return False

        # get value to check
        val_check = self.board[id]
        totalMatch = 0
        # check horizontally syre
        while(totalMatch < 3):
            id+=1
            if(self.board[id] != val_check):
                break
            
            totalMatch+=1
        
        if(totalMatch == 3):
            return True
        return False
    
    def check_vertical_win(self, id):        
        # get value to check
        val_check = self.board[id]
        # check vertically syre
        totalMatch = 0
        while totalMatch < 3:
            id+=7
            if(self.board[id] != val_check):
                break
            totalMatch+=1
        
        if(totalMatch==3):
            return True
        return False
    
    def check_positive_diagonal_win(self, id):
        if(id % 7 > 3):
            return False
        
        val_check = self.board[id]
        totalMatch = 0
        while totalMatch < 3:
            id -=6
            if(self.board[id] != val_check):
                break
            totalMatch+=1
        
        if(totalMatch==3):
            return True
        return False
    
    def check_negative_diagonal_win(self, id):
        if(id % 7 < 3):
            return False
        
        val_check = self.board[id]
        totalMatch = 0
        while totalMatch < 3:
            id -=8
            if(self.board[id] != val_check):
                break
            totalMatch+=1
        
        if(totalMatch==3):
            return True
        return False

    def check_win(self, i):
        isWin = False
        winner = 8# random non -1 or 1
        # if(self.board[i]==0):
        #     print("anjir kok 0")
        #     return False

        if(self.check_horizontal_win(i)):
            isWin = True
            winner = self.board[i]
            return isWin, winner

        if(i > 20):
            # check all diagonal
            if(self.check_negative_diagonal_win(i)):
                isWin=True
                winner = self.board[i]
                return isWin, winner
            if(self.check_positive_diagonal_win(i)):
                isWin=True
                winner = self.board[i]
                return isWin, winner
        else:
            if(self.check_vertical_win(i)):
                isWin=True
                winner = self.board[i]
                return isWin, winner

        return isWin, winner
    
    def fast_check_win(self):
        isWin = False
        winner = 8
        for col in range(self.total_col):
            if( isWin ):
                break

            for row in range(self.col_base[col]+1, 6):
                isWin, winner = self.check_win(self.TRANSFORM_1D[row][col])
                if(isWin):
                    break
        
        return isWin, winner


    def draw_board(self):
        for i in range(self.total_row):
            cy = i * self.block_size + self.half_size
            row_offset = i * self.total_col
            for j in range(self.total_col):
                cx = j * self.block_size + self.half_size
                pygame.draw.circle(self.window, self.COLOR_DICT[self.board[row_offset + j]], (cx, cy), self.half_size-5)
                

    def draw(self):
        self.window.fill(self.BG)
        self.draw_board()
    
    # Do a one game loop (move, update, draw)
    def loop(self, col_act):
        """
        Executes a single game loop.
        :returns: GameInformation instance
        """
        self.move(col_act)
        isWin, winner = self.fast_check_win()
        # 'draw' equal case

        isDraw = not isWin and len(self.history_move) == 42
        isWin = isWin or isDraw
        game_info = GameInformation(isWin, winner, isDraw)
        
        return game_info
    
    def reset(self):
        pass