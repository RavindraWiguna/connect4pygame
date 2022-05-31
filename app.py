import pygame
from connect_four.game import Game, GameInformation
import neat
from numpy import argmax
from neatUtils import visualize
from collections import Counter
import pickle
import os

'''
A Class of a single connect four
'''
class ConnectFourGame:
    def __init__(self, window, width, height, block_size, fps) -> None:
        self.game = Game(window, width, height, block_size)
        self.FPS = fps

    def test_ai(self, net:neat.nn.FeedForwardNetwork, human_turn:int):
        if(human_turn > 1 or human_turn < 0):
            raise ValueError("turn can only be between 0 or 1")

        isRunning = True
        clock = pygame.time.Clock()
        while(isRunning):
            for event in pygame.event.get():
                if(event.type == pygame.QUIT):
                    isRunning = False
                    break

            # Human Movement
            # right now still cli
            if(self.game.turn&1 == human_turn):
                col = int(input("where u wanna drop your disk?:"))
            
            else:
                # Computer Movement 
                comp_out = net.activate(self.game.board)
                col = argmax(comp_out)
            

            # Update the game conditions
            game_info = self.game.loop(col)
            # print(game_info.left_score, game_info.right_score)
            # Draw the game's frame
            self.game.draw()
            pygame.display.update()
            # sleep if needed to keep game running at 60 fps
            clock.tick(self.FPS)

            if(game_info.isWin):
                isRunning = False
                print(f"This player: {game_info.winner}, win")
        
        pygame.quit()
    
    def move_ai(self,net_turn:neat.nn.FeedForwardNetwork, 
                     genome_turn:neat.DefaultGenome):
            
            if(self.game.turn&1):
                # this is odd turn, a.k.a second player
                board = self.game.get_p2_pov()
            else:
                board = self.game.board
            
            comp_out = net_turn.activate(board)
            while True:
                col = argmax(comp_out)
                isValid = self.game.check_valid_move(col)
                if(not isValid):
                    comp_out[col] -= 1000
                    genome_turn.fitness -= 10
                else:
                    break

            return col

    def calculate_fitness(self, 
                          genome1:neat.DefaultGenome, 
                          genome2:neat.DefaultGenome, 
                          game_info:GameInformation):
        genome1.fitness += game_info.isWin *(game_info.winner == 1) * 250
        genome2.fitness += game_info.isWin *(game_info.winner == -1) * 250



    def train_ai(self, genome1, genome2, config, isDraw=False):
        isRunning = True
        isDone = False
        # Create the neural networks
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        players = [[net1, genome1], [net2, genome2]]
        while(isRunning):
            for event in pygame.event.get():
                if(event.type == pygame.QUIT):
                    isRunning = False
                    # we dont set is done to true because it is force to close
                    break
            
            col = self.move_ai(players[self.game.turn&1][0], players[self.game.turn&1][1])

            # Update the game conditions
            game_info = self.game.loop(col)
            # print(game_info.left_score, game_info.right_score)
            # Draw the game's frame
            if(isDraw):
                self.game.draw()   
                pygame.display.update()
            
            if game_info.isWin:
                self.calculate_fitness(genome1, genome2,game_info)
                isDone = True
                isRunning = False
                # believe in no break _/|\_
        
        # pygame.quit()
        return isDone

def eval_genomes(genomes, config):
    print("training genomes")
    """
    Run each genome against eachother one time to determine the fitness.
    """
    dict_fitness = Counter() # default value is 0 if never assigned
    BLOCK_SIZE = 100
    WIDTH, HEIGHT = 7*BLOCK_SIZE, 6*BLOCK_SIZE
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    for i, (genome_id1, genome1) in enumerate(genomes):
        # print the percentages of this net training progress
        print(round(i/len(genomes) * 100), end=" ")
        genome1.fitness = dict_fitness[genome_id1]
        # loop for genome in the index i+1 till end 
        # (don't worry it wont cause index error cause genomes[i+1: ] will always return a list, either with some items or none)
        for genome_id2, genome2 in genomes[i+1:]:
            genome2.fitness = dict_fitness[genome_id2]
            connect4 = ConnectFourGame(win, WIDTH, HEIGHT, BLOCK_SIZE, 60)
            peaceful_exit = connect4.train_ai(genome1, genome2, config, True)
            dict_fitness[genome_id1] = genome1.fitness
            dict_fitness[genome_id2] = genome2.fitness
            if(not peaceful_exit):
                quit()
        
        print(f'current fitness for {genome_id1}: {genome1.fitness}')
            

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)

    # Save the winner
    with open("best_genome.pickle", "wb") as saver:    
        pickle.dump(winner, saver, pickle.HIGHEST_PROTOCOL)
        print("WINNER IS SAVED on best_genome.pickle")
    
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))
    
    # Show output of the most fit genome against training data.
    # print('\nOutput:')
    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    # node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
    # visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    # To load from last check point (in case the training is stopped syre)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    # p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, './neatUtils/config-feedforward')
    run(config_path)
    # config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
    #                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
    #                     config_path)

    # winner_pickle = open(os.path.join(local_dir, "best_genome.pickle"), "rb")
    # winner = pickle.load(winner_pickle)
    # width, height = 640, 480
    # win = pygame.display.set_mode((width, height))
    # pong = PongGame(win, width, height, 60)
    
    # net = neat.nn.FeedForwardNetwork.create(winner, config)
    # pong.test_ai(net)
