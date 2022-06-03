from random import choice
import pygame
from connect_four.game import Game
from math import sqrt, log, inf
from time import time as curtime
from numexpr import evaluate

class MonteCarloNode:
    def __init__(self, historyMove:str, exploration_param, isPlayerOne:bool) -> None:
        self.total_child = 0
        self.total_score = 0
        self.total_visit = 0
        self.total_parrent_visit = 0
        self.c = exploration_param
        # game move history
        self.history = historyMove
        # array of total disk on each column of the board
        self.column_fill = [0, 0, 0, 0, 0, 0, 0]
        for move in self.history:
            self.column_fill[int(move)]+=1
        # this implementation cause the form of a tree even tho it is a graph, idk how to store it all efficiently mate
        self.children = [] # also a monte carlo node
        self.isPlayerOne = isPlayerOne
        self.move_to_child_id = {}
        self.child_id_to_move = {}
    
    def find_children(self):
        for i, total_disk in enumerate(self.column_fill):
            # print(self.column_fill) # for debug purpose
            # print(self.history) #is certified right
            if(total_disk < 6):
                # map move to child id
                self.move_to_child_id[i] = self.total_child
                # the exact reverse
                self.child_id_to_move[self.total_child] = i
                self.total_child+=1
                local_history = ''.join([self.history, str(i)])
                # print(f"history new: {local_history}, before: {self.history}, move: {i}")
                self.children.append(MonteCarloNode(local_history, self.c, self.isPlayerOne))
        
        # print(f"found {self.total_child} for {self.history}")

    def calculate_ucb(self):
        if(self.total_visit == 0):
            # never visited, return inf
            # print(f"this node {self.history} never visited")
            # print(f"inf: {self.history}")
            return inf
        
        # exploitation term is the average score
        # exploit_term = 
        # exploration term is this formula (still don't know why)
        # but the point is less visited => bigger score => more likely to be visited ==> exploration
        # explore_term = 
        # ucb_total =exploit_term + explore_term
        # print(f"ucb: {ucb_total}| {self.history}")
        return self.total_score/self.total_visit + self.c * sqrt(log(self.total_parrent_visit)/self.total_visit)
        # total_score, total_visit, c, total_parrent_visit = self.total_score, self.total_visit, self.c, self.total_parrent_visit
        # return evaluate("total_score/total_visit + c * sqrt(log(total_parrent_visit)/total_visit)")
    
    def update_children_parrent_visit(self):
        for i in range(self.total_child):
            self.children[i].total_parrent_visit +=1

'''
A Class of a single connect four player
'''
class ConnectFourMC:
    def __init__(self, time_limit) -> None:
        self.time_limit = time_limit
        self.max_depth = 0

    def selection(self, initState:MonteCarloNode):
        isTraversing = True
        current = initState
        # depth = 0
        while isTraversing:
            # depth+=1
            # dont ever find children here
            # check if current is leaf node
            if(current.total_child == 0):
                # break and lets go to expansion
                # print(f"found leaf node: {current.history}")
                isTraversing = False
                break

            # so it aint leaf
            current = max(current.children, key=lambda x: x.calculate_ucb())
        
        # print(f"giving:{current.history}")
        # if(self.max_depth < depth):
        #     self.max_depth = depth
        #     print(f"depth:{depth} ")
        return current


    def expansion(self, node:MonteCarloNode):
        node.find_children()
        return node.children[0]
        

    def simulation(self, node:MonteCarloNode):
        the_game = Game(None, 7, 6, 1)
        the_game.load_history(node.history)
        isNotOver = True
        game_info = None
        while isNotOver:
            game_info = the_game.loop(choice(the_game.get_available_move()))
            isNotOver = not game_info.isWin
        
        # not draw, first player win
        if(game_info.winner == 1):
            # some transform logic for relativity
            return 100 * (-1+ 2*node.isPlayerOne) * (not game_info.isDraw)
        # oh player 2 won
        return 100 * (1 -2*node.isPlayerOne)* (not game_info.isDraw)
        

        

    def backpropagation(self, init_state:MonteCarloNode, choosen:MonteCarloNode, score: int):
        current = init_state
        # print(f"before init {init_state.total_score}| {init_state.history}")
        start_path = len(init_state.history)
        while current.total_child != 0:
            # print(f"before1 {current.total_score}| {current.history}")
            current.total_visit +=1
            current.total_score += score
            
            current.update_children_parrent_visit()
            move = int(choosen.history[start_path])
            start_path+=1
            # print(f"after1 {current.total_score}| {current.history}")
            current = current.children[current.move_to_child_id[move]]
        

        # print("CHOOSEN UPDATE")
        current.total_visit +=1
        current.total_score += score
        # print(f"after choosen: {choosen.history}: {choosen.total_visit} | {choosen.total_score}")

    def get_best_move(self, node:MonteCarloNode):
        move = None
        curMax = -inf
        for i in range(node.total_child):
            local_avg_score = node.children[i].total_score/node.children[i].total_visit
            if(local_avg_score > curMax):
                curMax = local_avg_score
                move = node.child_id_to_move[i]
        
        return move



    def monte_carlo_search(self, historyMove, isPlayerOne):
        self.max_depth = 0
        print("monte carlo search start...")
        start_time = curtime()
        init_state = MonteCarloNode(historyMove, 2, isPlayerOne)
        # generate current tree
        init_state.find_children()
        # total_expand = init_state.total_child
        total_expand = 1
        # deepest = 0
        best_node = init_state.children[0]
        choosen = best_node
        # print(best_node.total_visit > 0 ^ (choosen.history == best_node.history))
        # print(best_node.total_visit > 0)
        # print((choosen.history == best_node.history))
        while((curtime() - start_time < self.time_limit)):
            # do monte carlo search
            # selection
            # print("start selection")
            best_node = self.selection(init_state)
            # print("start expansion or simul")
            # check expansion
            if(best_node.total_visit == 0):
                # we don't expand, we simulate
                # print("never visited!!!!!!!!!!!!!!")
                choosen = best_node
            else:
                # print("EXPAAAANDER")
                # ah already visited, so expand
                choosen = self.expansion(best_node)
                # deepest+=1
            total_expand += 1
            # print("start simul")
            # if(not (best_node.total_visit > 0) ^ (choosen.history == best_node.history)):
            #     break
            # ((best_node.total_visit > 0) ^ (choosen.history == best_node.history))
            simul_score = self.simulation(choosen)
            # now we back propagate
            # print("start back prop")
            self.backpropagation(init_state, choosen, simul_score)
            # print(best_node.total_visit > 0)
            # print((choosen.history == best_node.history))
        
        print(f"we have iterated: {total_expand}")
        return self.get_best_move(init_state)


def main():
    BLOCK_SIZE = 100
    WIDTH, HEIGHT = 7*BLOCK_SIZE, 6*BLOCK_SIZE
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(win, WIDTH, HEIGHT, BLOCK_SIZE)
    isRunning = True
    clock = pygame.time.Clock()
    bot = ConnectFourMC(15.0)
    game.draw()
    pygame.display.update()
    rangeCol = []
    for i in range(7):
        rangeCol.append((i*BLOCK_SIZE, (i+1)*BLOCK_SIZE))
    while isRunning:
        clock.tick(60)
        if(game.turn&1==0):
            # comp move
            col = bot.monte_carlo_search(game.get_history_move_str(), True)
            result = game.loop(col)
            print("end of bot")
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isRunning = False
                    break
                if(event.type == pygame.MOUSEBUTTONUP):
                    pos = pygame.mouse.get_pos()
                    # print(pos)
                    for i, bound in enumerate(rangeCol):
                        # print(bound)
                        if(pos[0] > bound[0] and pos[0] < bound[1]):
                            # print(f'i{i}')
                            col = i
                            break
                    # print(col)

                    result = game.loop(col)
                    
        

            
        
        game.draw()
        pygame.display.update()

        if(result.isWin):
            isRunning = False
            print(f"This player: {result.winner}, win")


if __name__=="__main__":
    main()
    # bot = ConnectFourMC(10.0)
    # game = Game(None, 7, 6, 1)
    # import cProfile
    # cProfile.run("bot.monte_carlo_search(game.get_history_move_str(), True)")


    