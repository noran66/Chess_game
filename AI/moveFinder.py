import random
import config
from .evaluation import scoreBoard, pieceScore

# Global variables to store the best move found and the search depth
nextMove = None
current_search_depth = 3 

"""
This is a simple function to find a random move.
Used as a fallback if the AI cannot find a better move.
"""
def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

"""
This is a helper method to make the first calls for the actual algorithm.
It initializes the global variables and starts the NegaMax search.
"""
def findBestMoveMinMax(gs, validMoves, returnQueue, depth):
    global nextMove, current_search_depth
    nextMove = None
    current_search_depth = depth # Update the global depth variable
    random.shuffle(validMoves)
    
    # Start the recursive search
    findMoveNegaMaxAlphaBeta(gs, validMoves, depth, -config.CHECKMATE, config.CHECKMATE, 1 if gs.whiteToMove else -1)
    
    # Return the best move found
    returnQueue.put(nextMove)

"""
Implementing the Nega-Max algorithm with Alpha-Beta pruning.
This function works recursively to find the best score for the current player.
"""
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    
    # Base case: if we reached the maximum depth, return the board evaluation
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # Move Ordering: Search better moves first to improve Alpha-Beta pruning efficiency
    orderedMoves = orderMoves(validMoves)
    maxScore = -config.CHECKMATE
    
    for move in orderedMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        
        # Recursive call: flip alpha and beta and negate the score
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        
        if score > maxScore:
            maxScore = score
            
            # The Trick: We only want to update the 'nextMove' if we are at the top level 
            # of the recursion tree (when current depth matches the search depth).
            if depth == current_search_depth: 
                nextMove = move
                
        gs.undoMove()
        
        # Alpha-Beta Pruning logic
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
            
    return maxScore

"""
Orders the moves list based on a heuristic score.
Logic used: MVV-LVA (Most Valuable Victim - Least Valuable Aggressor).
Meaning: Capturing a Queen with a Pawn is better than capturing a Pawn with a Queen.
"""
def orderMoves(moves):
    def moveScore(move):
        score = 0
        if move.isCapture:
            # Get the value of the piece being captured (The Victim)
            victimValue = pieceScore.get(move.pieceCaptured[1], 0)
            
            # Get the value of the piece moving (The Aggressor)
            attackerValue = pieceScore.get(move.pieceMoved[1], 0)
            
            # Heuristic Formula: 10 * Victim - Aggressor
            score = 10 * victimValue - attackerValue
            
        return score

    # Sort the moves in descending order (highest score first)
    moves.sort(key=moveScore, reverse=True)
    return moves