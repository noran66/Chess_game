import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

'''
Find the best move looking two steps ahead (Minimax Depth 2)
'''
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    maxScore = -CHECKMATE
    bestMove = None
    random.shuffle(validMoves)

    for playerMove in validMoves:
        gs.make_move(playerMove)
        
        # Check if the move leads to an immediate win
        if gs.checkMate:
            score = CHECKMATE
        elif gs.staleMate:
            score = STALEMATE
        else:
            # If game continues, simulate opponent's best response
            opponentMoves = gs.getValidMoves()
            minOpponentScore = CHECKMATE 
            
            for oppMove in opponentMoves:
                gs.make_move(oppMove)
                if gs.checkMate:
                    score = -CHECKMATE 
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = scoreMaterial(gs.board) * turnMultiplier
                
                # Opponent chooses the move that gives us the lowest score
                if score < minOpponentScore:
                    minOpponentScore = score
                gs.undoMove()
            
            score = minOpponentScore

        # We choose the move that gives us the highest score after opponent's response
        if score > maxScore:
            maxScore = score
            bestMove = playerMove
            
        gs.undoMove()
        
    return bestMove

'''
score the board based on material
'''

def scoreMaterial(board):
    score =0 
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score