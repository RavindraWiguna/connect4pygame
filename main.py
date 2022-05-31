import pygame
from connect_four.game import Game

def main():
    BLOCK_SIZE = 100
    WIDTH, HEIGHT = 7*BLOCK_SIZE, 6*BLOCK_SIZE
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(win, WIDTH, HEIGHT, BLOCK_SIZE)
    isRunning = True
    clock = pygame.time.Clock()
    game.draw()
    pygame.display.update()
    while isRunning:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
                break
        
        col = int(input("col: "))
        result = game.loop(col)
        game.draw()
        pygame.display.update()

        if(result.isWin):
            isRunning = False
            print(f"This player: {result.winner}, win")


main()