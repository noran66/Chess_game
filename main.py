"""
This is our main driver. It will be responsible for handling user input
and displaying the current GameState object.
"""

import pygame as p
import Engine
import SmartMoveFinder
from Engine import *
from SmartMoveFinder import *
import os

# --- Dimensions and Colors Configuration ---
BOARD_WIDTH = BOARD_HEIGHT = 512
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}

# UI Colors (Modern Theme with Red Highlights)
COLORS = {
    'light': p.Color(234, 235, 200),
    'dark': p.Color(119, 148, 85),
    'highlight': p.Color(186, 202, 43),  # Yellow-Green for normal moves
    'capture': p.Color(235, 90, 90),     # Red for capture moves
    'check': p.Color(255, 0, 0),         # Bright Red for King in check
    'move_trace': p.Color(246, 246, 105)
}

"""
Initialize a global dictionary of images. This will be called exactly once in the main.
"""
def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        if os.path.exists(os.path.join("images", piece + ".png")):
            IMAGES[piece] = p.transform.scale(p.image.load(os.path.join("images", piece + ".png")), (SQ_SIZE, SQ_SIZE))
        else:
            # Fallback if image not found (prevents crash)
            print(f"Warning: Image for {piece} not found.")

def main():
    p.init()
    # Set screen size to accommodate ONLY the board (Removed Panel Width)
    screen = p.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    gs = Engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False   # flag variable for when we should animate a move
    load_images()  # only do this once, before the while loop
    
    Running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple: (row,col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False # flag variable for when the game ends
    playerOne = True # If a Human is playing white, then this will be True. If AI is playing this will be False
    playerTwo = False # Same as above but for black

    while Running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                Running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    
                    if sqSelected == (row, col):  # the user clicked the same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                    
                    if len(playerClicks) == 2:  # after 2nd click
                        move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.get_chess_notation())
                        
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if validMoves[i].isPawnPromotion:
                                    # Handle pawn promotion choice
                                    choice = showPromotionChoices(screen, validMoves[i], p.font.SysFont("Arial", 24, True, False))
                                    validMoves[i].promotedPiece = choice 
                                gs.make_move(validMoves[i])
                                moveMade = True
                                animate = True 
                                sqSelected = () 
                                playerClicks = []
                                break 
                        
                        if not moveMade:
                            playerClicks = [sqSelected]
            
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False # reset game over on undo
                if e.key == p.K_r: # reset when 'r' is pressed
                    gs = Engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
        
        # AI move finder
        if not gameOver and not humanTurn and not moveMade:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.make_move(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        
        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.inCheck:
            if len(validMoves) == 0:
                gameOver = True
                drawEndGameText(screen, 'Black Wins' if gs.whiteToMove else 'White Wins')
        elif len(validMoves) == 0:
            gameOver = True
            drawEndGameText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Pawn promotion choice display and handling
'''
def showPromotionChoices(screen, move, headerFont):
    # Dim the background
    overlay = p.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    overlay.set_alpha(100)
    overlay.fill(p.Color("black"))
    screen.blit(overlay, (0,0))
    
    # Get piece color and prepare choice images
    color = move.pieceMoved[0] # 'w' or 'b'
    choices = ['Q', 'R', 'B', 'N']
    choiceImages = [IMAGES[color + piece] for piece in choices]
    
    # --- UI Adjustment for Spacing ---
    popupWidth = 360  # Increased width to fit all pieces
    popupHeight = SQ_SIZE + 50
    
    # Center the popup on screen
    selectionRect = p.Rect((BOARD_WIDTH - popupWidth) // 2, (BOARD_HEIGHT - popupHeight) // 2, popupWidth, popupHeight)
    
    p.draw.rect(screen, p.Color("white"), selectionRect)
    p.draw.rect(screen, p.Color("black"), selectionRect, 2) # Border
    
    # Draw header text centered
    text = headerFont.render("Promote to:", True, p.Color("black"))
    textRect = text.get_rect(center=(selectionRect.centerx, selectionRect.y + 20))
    screen.blit(text, textRect)
    
    # Draw choice buttons
    buttonRects = []
    padding_left = 10  # Adjusted padding
    spacing = 10       # Adjusted spacing
    start_y = selectionRect.y + 50
    
    for i, img in enumerate(choiceImages):
        x = selectionRect.x + padding_left + (i * (SQ_SIZE + spacing))
        y = start_y
        screen.blit(img, (x, y))
        buttonRects.append(p.Rect(x, y, SQ_SIZE, SQ_SIZE))
    
    p.display.flip()
    
    # Wait for user to click on one of the choices
    while True:
        for e in p.event.get():
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                for i, rect in enumerate(buttonRects):
                    if rect.collidepoint(location):
                        return choices[i] # Return the chosen piece

'''
Highlight squares selected and moves for piece selected.
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    # 1. Highlight King if in Check (Always visible)
    if gs.inCheck:
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(150) # Higher alpha for check to be very visible
        s.fill(COLORS['check'])
        if gs.whiteToMove:
            screen.blit(s, (gs.whiteKingLocation[1] * SQ_SIZE, gs.whiteKingLocation[0] * SQ_SIZE))
        else:
            screen.blit(s, (gs.blackKingLocation[1] * SQ_SIZE, gs.blackKingLocation[0] * SQ_SIZE))

    # 2. Highlight Selected Piece and Valid Moves
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            
            # highlight moves from that square
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    # Check if it's a capture move
                    if move.pieceCaptured != '--' or move.isEnPassantMove:
                        s.fill(COLORS['capture']) # Red for capture
                    else:
                        s.fill(COLORS['highlight']) # Yellow/Green for normal move
                    
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

''' 
Responsible for all the graphics within a current game state.
'''    
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) 
    # REMOVED: drawMoveLog call

'''
Draw the squares on the board.
'''
def drawBoard(screen):
    colors = [COLORS['light'], COLORS['dark']]
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

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    colors = [COLORS['light'], COLORS['dark']]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnPassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

'''
Draw end game text
'''
def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2, BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()