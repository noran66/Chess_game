"""
This is our main driver. It will be responsible for handling user input
and displaying the current GameState object.
"""

import pygame as p
import Engine
import SmartMoveFinder
from Engine import *
from SmartMoveFinder import *
import pygame as p
import os
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512  
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}

"""
Initialize a global dictionary of images. This will be called exactly once in the main.
"""

def load_images():
    
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
            IMAGES[piece] = p.transform.scale(p.image.load(os.path.join("images", piece + ".png")), (SQ_SIZE, SQ_SIZE))
    
def main():
        p.init()
        screen = p.display.set_mode((WIDTH, HEIGHT))
        clock = p.time.Clock()
        screen.fill(p.Color("white"))
        gs = Engine.GameState()
        load_images()  # only do this once, before the while loop
        Running = True
        while Running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    Running = False
            drawGameState(screen, gs)
            clock.tick(MAX_FPS)
            p.display.flip()
''' 
Responsible for all the graphics within a current game state.
'''   
def drawGameState(screen,gs):
        drawBoard(screen)  
        drawPieces(screen, gs.board)  

'''
Draw the squares on the board. the top left square is always light.
'''

def drawBoard(screen):
    colors = [p.Color("white"), (118, 150, 86)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    

'''
Draw the pieces on the board using the current GameState.board
'''

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    

if __name__ == "__main__":
    main()