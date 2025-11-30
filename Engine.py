"""
This is responsiwle for storing all the information about the current state
of the chess game. Also, be responsible for determining the valid moves at
the current state. And it'll keep a move log.
"""

class GameState:
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'.
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', or 'P'.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
    '''
     Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant)
    '''
    def make_move(self, move):
        self.board[move.startrow][move.startcol] = "--"
        self.board[move.endrow][move.endcol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
    '''
     Undo the last move made.
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startrow][move.startcol] = move.pieceMoved
            self.board[move.endrow][move.endcol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back
    '''
     All moves considering checks
    '''
    def getValidMoves(self):
        return self.getAllPossibleMoves() # for now we will not worry about checks
    '''
     All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            # number of columns in a given row
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # the piece color
                
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    
                    piece = self.board[r][c][1]  
                    if piece == "P":
                        self.getPawnMoves(r, c, moves)
                    elif piece == "R":
                        self.getRookMoves(r, c, moves)
                    elif piece == "N":
                        self.getKnightMoves(r, c, moves)
                    elif piece == "B":
                        self.getBishopMoves(r, c, moves)
                    elif piece == "Q":
                        self.getQueenMoves(r, c, moves)
                    elif piece == "K":
                        self.getKingMoves(r, c, moves)
                        

        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list 
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # white pawn moves
            if self.board[r-1][c] == "--" and r-1 >= 0: #the square in front is empty
                moves.append(Move((r, c), (r-1, c), self.board)) # 1 square ahead
                if r == 6 and self.board[r-2][c] == "--": # starting square and 2 squares ahead is empty
                    moves.append(Move((r, c), (r-2, c), self.board)) # 2 squares ahead
            # captures
            if c-1>=0: # capture to the left
                if self.board[r-1][c-1][0] == "b": # there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1<=7: # capture to the right
                if self.board[r-1][c+1][0] == "b": # there is an enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else: # black pawn moves
            if self.board[r+1][c] == "--" and r+1 <=7: #the square in front is empty
                moves.append(Move((r, c), (r+1, c), self.board)) # 1 square ahead
                if r == 1 and self.board[r+2][c] == "--": # starting square and 2 squares ahead is empty
                    moves.append(Move((r, c), (r+2, c), self.board)) # 2 squares ahead
            # captures
            if c-1>=0: # capture to the left
                if self.board[r+1][c-1][0] == "w": # there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1<=7: # capture to the right
                if self.board[r+1][c+1][0] == "w": # there is an enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
    '''
    Get all the rook moves for the rook located at row, col and add these moves to
    the list 
    '''
    def getRookMoves(self, r, c, moves):
        if self.whiteToMove: # white rook moves
            directions = [(-1, 0), (0, -1), (1, 0), (0, 1)] # up, left, down, right
            for d in directions:
                for i in range(1, 8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # empty square
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == "b": # enemy piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # friendly piece
                            break
                    else: # off board
                        break
        else: # black rook moves
            directions = [(-1, 0), (0, -1), (1, 0), (0, 1)] # up, left, down, right
            for d in directions:
                for i in range(1, 8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # empty square
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == "w": # enemy piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # friendly piece
                            break
                    else: # off board
                        break
    '''
    Get all the knight moves for the knight located at row, col and add these moves to
    the list 
    '''    
    def getKnightMoves(self, r, c, moves):
        pass
    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to
    the list 
    ''' 
    def getBishopMoves(self, r, c, moves):
        pass
    '''
    Get all the queen moves for the queen located at row, col and add these moves to
    the list
    '''
    def getQueenMoves(self, r, c, moves):
        pass
    '''
    Get all the king moves for the king located at row, col and add these moves to
    the list 
    ''' 
    def getKingMoves(self, r, c, moves):
        pass
class Move:
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board):
        self.startrow = startSq[0]
        self.startcol = startSq[1]
        self.endrow = endSq[0]
        self.endcol = endSq[1]
        self.pieceMoved = board[self.startrow][self.startcol]
        self.pieceCaptured = board[self.endrow][self.endcol]
        
        self.moveID = self.startrow * 1000 + self.startcol * 100 + self.endrow * 10 + self.endcol
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
        
    def get_chess_notation(self):
        # You can make this like real chess notation later
        return self.get_rank_file(self.startrow, self.startcol) + self.get_rank_file(self.endrow, self.endcol)
        
        
    def get_rank_file(self, r, c):
        # return rank and file notation
        return self.colsToFiles[c] + self.rowsToRanks[r]
        
    
        

    