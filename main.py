import sys
import os
from multiprocessing import Process, Queue
import pygame as p

# --- Import Project Files ---
import config
from Engine.gameState import GameState
from Engine.move import Move
from AI import moveFinder

# --- Path Setup ---
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

# --- Global Variables ---
IMAGES = {}

"""
As loading the images can be a costly process, we need to
initialize a global dictionary for images just once in the main.
"""
def loadImages():
    pieces = ["wp", "wN", "wB", "wR", "wQ", "wK", "bp", "bN", "bB", "bR", "bQ", "bK"]
    for piece in pieces:
        img = os.path.join(image_path, piece + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(img), (config.SQ_SIZE, config.SQ_SIZE))

"""
The following is the driver of our code which will handle user inputs and updating the graphics
"""
def main():
    p.init()
    p.display.set_caption("Chess AI - Noran")
    screen = p.display.set_mode((config.BOARD_WIDTH, config.BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    
    # Initialize Fonts
    moveLogFont = p.font.SysFont("Arial", 20, False, False)
    menuFont = p.font.SysFont("Arial", 24, True, False) # Font for the menu
    
    # Initialize Game State
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    
    loadImages() # Load images once
    
    running = True
    sqSelected = ()      # Keep track of the last click of the user (tuple: (row, col))
    playerClicks = []    # Keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False

    # Player Configuration
    playerOne = False   # If a human is playing white, this will be True
    playerTwo = False  # If a human is playing black, this will be True (False means AI)

    # AI Variables
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    # --- Difficulty Setup ---
    current_difficulty = config.DIFFICULTY['MEDIUM'] # Default difficulty

    # --- Menu Variable ---
    gameStarted = False # Flag to check if the game has started or we are in the menu

    # --- Game Loop ---
    while running:
        
        # -----------------------------------------
        # MODE 1: MENU SCREEN (If game hasn't started)
        # -----------------------------------------
        if not gameStarted:
            # Draw the menu and get button rectangles for collision detection
            easyBtn, mediumBtn, hardBtn = drawMenu(screen, menuFont)
            
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    
                    # Check which button was clicked
                    if easyBtn.collidepoint(location):
                        current_difficulty = config.DIFFICULTY['EASY']
                        print("Easy Mode Selected")
                        gameStarted = True # Start the game
                    elif mediumBtn.collidepoint(location):
                        current_difficulty = config.DIFFICULTY['MEDIUM']
                        print("Medium Mode Selected")
                        gameStarted = True
                    elif hardBtn.collidepoint(location):
                        current_difficulty = config.DIFFICULTY['HARD']
                        print("Hard Mode Selected")
                        gameStarted = True
            
            p.display.flip()
            continue # Skip the rest of the loop until a difficulty is selected

        # -----------------------------------------
        # MODE 2: CHESS GAME (If game has started)
        # -----------------------------------------
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # --- Mouse Handling ---
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # (x, y) location of mouse
                    col = location[0] // config.SQ_SIZE
                    row = location[1] // config.SQ_SIZE
                    
                    # The user clicked the same square twice or clicked outside the board
                    if sqSelected == (row, col) or col >= 8: 
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    # After the second click, we need to make the move
                    if len(playerClicks) == 2: 
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                targetMove = validMoves[i]
                                # Pawn Promotion Handling
                                if targetMove.isPawnPromotion:
                                    promotedType = userSelectPromotion(screen, gs, targetMove)
                                    targetMove.promotedPiece = promotedType
                                
                                gs.makeMove(targetMove)
                                moveMade = True
                                animate = True
                                sqSelected = () # Reset for next turn
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # --- Key Handling ---
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                
                elif e.key == p.K_r: # Reset board when 'r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = False
                    # Optional: Set gameStarted = False here if you want 'r' to go back to the menu

        # --- AI Turn Logic ---
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue() # Used to pass data between threads
                moveFinderProcess = Process(
                    target=moveFinder.findBestMoveMinMax,
                    args=(gs, validMoves, returnQueue, current_difficulty)
                )
                moveFinderProcess.start()
                
                # Note: This is blocking, but keeps logic simple as requested.
                AIMove = returnQueue.get()
                
                if AIMove is None:
                    AIMove = moveFinder.findRandomMoves(validMoves)
                
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        # Generate new set of valid moves
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        # Check for Game Over (Checkmate / Stalemate)
        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = "Stalemate" if gs.stalemate else ("Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate")
            drawEndGameText(screen, text)

        clock.tick(config.MAX_FPS)
        p.display.flip()


# ---------------------------------------------------
# Graphic & UI Functions
# ---------------------------------------------------

"""
Responsible for all the graphics needed for the current game state
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on top of squares
    # drawMoveLog(screen, gs, moveLogFont) # Disabled as requested

def drawBoard(screen):
    global colors
    colors = config.COLORS
    font = p.font.SysFont("Arial", 14, True, False)

    for r in range(config.DIMENSION):
        for c in range(config.DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * config.SQ_SIZE, r * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))
            
            # Draw coordinates (Ranks and Files)
            if c == 0:
                colorText = colors[0] if color == colors[1] else colors[1]
                label = font.render(str(8 - r), True, colorText)
                screen.blit(label, (c * config.SQ_SIZE + 2, r * config.SQ_SIZE + 2))
            
            if r == 7:
                colorText = colors[0] if color == colors[1] else colors[1]
                label = font.render(chr(ord('a') + c), True, colorText)
                screen.blit(label, (c * config.SQ_SIZE + config.SQ_SIZE - 12, r * config.SQ_SIZE + config.SQ_SIZE - 15))

"""
Highlight the square selected and valid moves for the piece selected
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    # 1. Highlight the last move made to help players see opponent's action
    # if len(gs.moveLog) > 0:
    #     lastMove = gs.moveLog[-1]
    #     s = p.Surface((config.SQ_SIZE, config.SQ_SIZE))
    #     s.set_alpha(100)
    #     s.fill(p.Color("green"))
    #     screen.blit(s, (lastMove.startCol * config.SQ_SIZE, lastMove.startRow * config.SQ_SIZE))
    #     screen.blit(s, (lastMove.endCol * config.SQ_SIZE, lastMove.endRow * config.SQ_SIZE))

    # 2. Highlight the King in Red if in Check
    if gs.inCheck:
        s = p.Surface((config.SQ_SIZE, config.SQ_SIZE))
        s.set_alpha(150)
        s.fill(p.Color("red"))
        if gs.whiteToMove:
            r, c = gs.whiteKingLocation
        else:
            r, c = gs.blackKingLocation
        screen.blit(s, (c * config.SQ_SIZE, r * config.SQ_SIZE))

    # 3. Highlight selected square and valid moves
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((config.SQ_SIZE, config.SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * config.SQ_SIZE, r * config.SQ_SIZE))
            
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if move.isCapture:
                        s.fill(p.Color("red"))
                    else:
                        s.fill(p.Color("yellow"))
                    screen.blit(s, (move.endCol * config.SQ_SIZE, move.endRow * config.SQ_SIZE))

def drawPieces(screen, board):
    for r in range(config.DIMENSION):
        for c in range(config.DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * config.SQ_SIZE, r * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(config.BOARD_WIDTH, 0, config.MOVE_LOG_PANEL_WIDTH, config.MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)
    
    padding = 5
    textY = padding
    lineSpacing = 5
    movesPerRow = 3
    
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j] + "  "
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, config.BOARD_WIDTH, config.BOARD_HEIGHT).move(
        config.BOARD_WIDTH / 2 - textObject.get_width() / 2,
        config.BOARD_HEIGHT / 2 - textObject.get_height() / 2,
    )
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

"""
The animation function
"""
def animateMove(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("light blue")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    
    for frame in range(frameCount + 1):
        r, c = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount,
        )
        drawBoard(screen)
        drawPieces(screen, board)
        
        # Erase the move from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * config.SQ_SIZE, move.endRow * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        
        # Draw the captured piece back onto the top of the rect
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enpassantRow = (move.endRow + 1) if move.pieceCaptured[0] == "b" else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * config.SQ_SIZE, enpassantRow * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        
        # Draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * config.SQ_SIZE, r * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))
        p.display.flip()
        clock.tick(120)

"""
Display a popup menu to let the user choose the promotion piece.
It halts the game loop until a selection is made.
"""
def userSelectPromotion(screen, gs, move):
    color = move.pieceMoved[0]
    promotionPieces = ["Q", "R", "B", "N"]
    direction = 1 if move.endRow == 0 else -1
    
    while True:
        for i, pieceCode in enumerate(promotionPieces):
            rowPos = move.endRow + (i * direction)
            colPos = move.endCol
            p.draw.rect(screen, p.Color("white"), p.Rect(colPos * config.SQ_SIZE, rowPos * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))
            pieceImage = IMAGES[color + pieceCode]
            screen.blit(pieceImage, p.Rect(colPos * config.SQ_SIZE, rowPos * config.SQ_SIZE, config.SQ_SIZE, config.SQ_SIZE))
        
        p.display.flip()
        
        for e in p.event.get():
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                clickRow = location[1] // config.SQ_SIZE
                clickCol = location[0] // config.SQ_SIZE
                
                if clickCol == move.endCol:
                    clickedIndex = (clickRow - move.endRow) * direction
                    if 0 <= clickedIndex < len(promotionPieces):
                        return promotionPieces[int(clickedIndex)]

"""
Display a popup menu to let the user choose the difficulty
"""
def drawMenu(screen, font):
    screen.fill(p.Color("black"))
    
    # Title
    titleFont = p.font.SysFont("Arial", 40, True, False)
    title = titleFont.render("Select Difficulty", True, p.Color("white"))
    titleRect = title.get_rect(center=(config.BOARD_WIDTH // 2, 100))
    screen.blit(title, titleRect)
    
    # Button Dimensions
    buttonWidth, buttonHeight = 200, 50
    centerX = config.BOARD_WIDTH // 2
    
    # Easy Button
    easyRect = p.Rect(0, 0, buttonWidth, buttonHeight)
    easyRect.center = (centerX, 200)
    p.draw.rect(screen, p.Color("green"), easyRect)
    text = font.render("Easy", True, p.Color("black"))
    textRect = text.get_rect(center=easyRect.center)
    screen.blit(text, textRect)
    
    # Medium Button
    mediumRect = p.Rect(0, 0, buttonWidth, buttonHeight)
    mediumRect.center = (centerX, 300)
    p.draw.rect(screen, p.Color("yellow"), mediumRect)
    text = font.render("Medium", True, p.Color("black"))
    textRect = text.get_rect(center=mediumRect.center)
    screen.blit(text, textRect)
    
    # Hard Button
    hardRect = p.Rect(0, 0, buttonWidth, buttonHeight)
    hardRect.center = (centerX, 400)
    p.draw.rect(screen, p.Color("red"), hardRect)
    text = font.render("Hard", True, p.Color("black"))
    textRect = text.get_rect(center=hardRect.center)
    screen.blit(text, textRect)
    
    return easyRect, mediumRect, hardRect

if __name__ == "__main__":
    main()