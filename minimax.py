from flippy import getValidMoves, makeMove, getScoreOfBoard
import sys, copy

WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value

# minimax tree search algorithm: here white is the maximising player and black is the minimising player
# depth is the search depth remaining, decremented for recursive calls
# alpha and beta are the bounds on viable play values used in alpha-beta pruning
def minimax(board, depth, tile, alpha, beta, evaluation):
    """
    Minimax function which searches game tree of a given depth. It returns the value of the best move according to an evaluation 
    function. 

    Args:
        board: 2D array containing the current board state
        depth: remaining search depth; the number of turns into the future we want to analyse
        tile: the colour of the tile which indicates whose turn it is
        alpha: 'alpha' parameter in alpha-beta pruning
        beta: 'beta' parameter in alpha-beta pruning
        evaluation: the evaluation function used to evaluate the board state at depth 0

    Returns:
        A number (usually a float) which indicates who is winning the game assuming optimal play for both players after searching
        through the game tree down to the specified depth.
    """
    # Firstly check whether the game has ended as of the most recent move; then can give definite valuation:
    gameState = checkGameOver(board)
    if gameState == 'WHITE':
        return sys.maxsize # return arbitrarily large value so that we know we have found a winning/losing sequence of moves.
    elif gameState == 'BLACK':
        return -sys.maxsize
    elif gameState == 'TIE':
        return 0 
    else:
        pass # No game condition met, continue searching down the decision tree.
    if depth == 0: # recursion base case
        return evaluation(board) # eval function which returns board value.

    # While recursion occurs: function alternates between going through the if BLACK_TILE and if WHITE_TILE code
    if tile == WHITE_TILE:
        maxScore = -sys.maxsize # initialise with worst possible score
        possibleMoves = getValidMoves(board, tile)
        possibleMoves = orderMoves(board, possibleMoves) # Roughly order moves to speed up alpha-beta pruning
        if possibleMoves == []:
            # If at some point during the game tree search, we find that we have no more moves, have to change 
            # tiles and then let the opponent play all their possible moves, then we continue once we again have some 
            # valid moves.
            maxScore = minimax(board, depth, BLACK_TILE, alpha, beta, evaluation)
        else:
            for x, y in possibleMoves:
                dupeBoard = copy.deepcopy(board)
                makeMove(dupeBoard, tile, x, y) # Get the new board state
                score = minimax(dupeBoard, depth - 1, BLACK_TILE, alpha, beta, evaluation)
                maxScore = max(maxScore, score)
                alpha = max(alpha, maxScore)
                if beta <= alpha:
                    break
        return maxScore
    
    else: # i.e. if black's turn
        # Symmetric to above code
        minScore = sys.maxsize
        possibleMoves = getValidMoves(board, tile)
        possibleMoves = orderMoves(board, possibleMoves)
        if possibleMoves == []:
            minScore = minimax(board, depth, WHITE_TILE, alpha, beta, evaluation)
        else:
            for x, y in possibleMoves:
                dupeBoard = copy.deepcopy(board)
                makeMove(dupeBoard, tile, x, y) # Get the new board state
                score = minimax(dupeBoard, depth - 1, WHITE_TILE, alpha, beta, evaluation)
                minScore = min(minScore, score)
                beta = min(beta, minScore)
                if beta <= alpha:
                    break
        return minScore
    
def minimaxMove(board, depth, tile, alpha, beta, evaluation):
    # Returns the move which has the best value according to minimax algorithm. White is the max player, black is the min.
    bestMaxValue = float("-inf")
    bestMinValue = float("inf")
    possibleMoves = getValidMoves(board, tile)
    possibleMoves = orderMoves(board, possibleMoves)
    for x, y in possibleMoves:
        # Think have to redefine board on each iteration to reset the board back to the root node of the tree.
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, tile, x, y) # Make the move and then go into the tree
        # Opponent makes the next move
        opponentTile = list(set([BLACK_TILE, WHITE_TILE]) - set([str(tile)]))[0] # Needs to be str, not in ' '
        moveValue = minimax(dupeBoard, depth, opponentTile, alpha, beta, evaluation) # Apply minimax algorithm
        if tile == WHITE_TILE:
            if moveValue > bestMaxValue:
                bestMove = [x, y]
                bestMaxValue = moveValue
        else:
            if moveValue < bestMinValue:
                bestMove = [x, y]
                bestMinValue = moveValue
    return bestMove
    
def checkGameOver(board):
    # Function which checks whether the game is over. Returns the winner as a string.
    # The game is over if neither player has any valid moves.
    whiteMoves = getValidMoves(board, WHITE_TILE)
    if whiteMoves: # this checks for an empty list
        return 'NOBODY'
    blackMoves = getValidMoves(board, BLACK_TILE)
    if blackMoves:
        return 'NOBODY'
    # If make it this far then neither player has any moves
    return declareWinner(board)

def declareWinner(board):
    # Function which finds the winner once the game is over.
    scores = getScoreOfBoard(board)
    if scores['BLACK_TILE'] > scores['WHITE_TILE']:
        return 'BLACK'
    elif scores['BLACK_TILE'] < scores['WHITE_TILE']:
        return 'WHITE'
    elif scores['BLACK_TILE'] == scores['WHITE_TILE']:
        return 'TIE'
    else:
        print("Something wrong!")
        return "Error!!"
        
def evaluation1(board):
    # Simple evaluation function which maximises the score difference.
    scores = getScoreOfBoard(board)
    return scores['WHITE_TILE'] - scores['BLACK_TILE']

def orderMoves(board, movesList):
    """
    This function estimates which moves will be best by ordering them based on DynamicRoxanne3's gameplay strategy. I.e.
    order the moves in the order that DynamicRoxanne3 would play.
    """
    originalRoxanneMatrix = [[1,5,3,3,3,3,5,1],
                [5,5,4,4,4,4,5,5],
                [3,4,2,2,2,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,2,2,2,4,3],
                [5,5,4,4,4,4,5,5],
                [1,5,3,3,3,3,5,1]]
    
    if board[0][0] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[0][1] = 2
        originalRoxanneMatrix[1][1] = 2
        originalRoxanneMatrix[1][0] = 2   
    if board[7][0] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[6][0] = 2
        originalRoxanneMatrix[7][1] = 2
        originalRoxanneMatrix[6][1] = 2
    if board[0][7] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[1][7] = 2
        originalRoxanneMatrix[0][6] = 2
        originalRoxanneMatrix[1][6] = 2
    if board[7][7] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[7][6] = 2
        originalRoxanneMatrix[6][7] = 2
        originalRoxanneMatrix[6][6] = 2
        
    # Just need to assign each move and index and then order the moves based on their assigned indices.
    assignments = {}
    for x, y in movesList:
        move = (x, y)
        assignments[move] = originalRoxanneMatrix[x][y]
        
    orderedMoves = dict(sorted(assignments.items(), key=lambda item: item[1]))
    # Fine to return a dictionary that has the Roxanne values; x, y in the for loop still gets the move coordinates.
    return orderedMoves

def cornerOccupancy(board):
    # Heuristic function which returns the heuristic value based on which corners are occupied. Corners are good so this
    # should be positive for white, the max player in our case.
    whiteCornerTiles, blackCornerTiles = 0, 0
    # Check the occupancy of the corners:
    if board[0][0] == WHITE_TILE:
        whiteCornerTiles += 1
    elif board[0][0] == BLACK_TILE:
        blackCornerTiles += 1
    if board[0][7] == WHITE_TILE:
        whiteCornerTiles += 1
    elif board[0][7] == BLACK_TILE:
        blackCornerTiles += 1
    if board[7][0] == WHITE_TILE:
        whiteCornerTiles += 1
    elif board[7][0] == BLACK_TILE:
        blackCornerTiles += 1
    if board[7][7] == WHITE_TILE:
        whiteCornerTiles += 1
    elif board[7][7] == BLACK_TILE:
        blackCornerTiles += 1
    # Heuristic normalised so that it ranges from -100 to 100. +1 in denominator to avoid division by 0 error.
    cornersOccupiedHeuristic = 100*(whiteCornerTiles - blackCornerTiles)/(whiteCornerTiles + blackCornerTiles + 1)
    return cornersOccupiedHeuristic

def cornerCloseness(board):
    # Heuristic function which returns the heuristic value based on which of the squares adjacent to the corners are 
    # occupied. Usually occupying these squares is bad idea, so this heuristic should be negative for white.
    whiteTiles, blackTiles = 0, 0
    # First check the occupancy of the squares adjacent to the corners, the 'X squares'.
    if board[0][0] == EMPTY_SPACE:
        if board[0][1] == WHITE_TILE:
            whiteTiles += 1
        elif board[0][1] == BLACK_TILE:
            blackTiles += 1
        if board[1][0] == WHITE_TILE:
            whiteTiles += 1
        elif board[1][0] == BLACK_TILE:
            blackTiles += 1
        if board[1][1] == WHITE_TILE:
            whiteTiles += 1
        elif board[1][1] == BLACK_TILE:
            blackTiles += 1
    if board[0][7] == EMPTY_SPACE:
        if board[0][6] == WHITE_TILE:
            whiteTiles += 1
        elif board[0][6] == BLACK_TILE:
            blackTiles += 1
        if board[1][6] == WHITE_TILE:
            whiteTiles += 1
        elif board[1][6] == BLACK_TILE:
            blackTiles += 1
        if board[1][7] == WHITE_TILE:
            whiteTiles += 1
        elif board[1][7] == BLACK_TILE:
            blackTiles += 1
    if board[7][0] == EMPTY_SPACE:
        if board[7][1] == WHITE_TILE:
            whiteTiles += 1
        elif board[7][1] == BLACK_TILE:
            blackTiles += 1
        if board[6][0] == WHITE_TILE:
            whiteTiles += 1
        elif board[6][0] == BLACK_TILE:
            blackTiles += 1
        if board[6][1] == WHITE_TILE:
            whiteTiles += 1
        elif board[6][1] == BLACK_TILE:
            blackTiles += 1
    if board[7][7] == EMPTY_SPACE:
        if board[7][6] == WHITE_TILE:
            whiteTiles += 1
        elif board[7][6] == BLACK_TILE:
            blackTiles += 1
        if board[6][6] == WHITE_TILE:
            whiteTiles += 1
        elif board[6][6] == BLACK_TILE:
            blackTiles += 1
        if board[6][7] == WHITE_TILE:
            whiteTiles += 1
        elif board[6][7] == BLACK_TILE:
            blackTiles += 1
    cornerClosenessHeuristic = -100*(whiteTiles - blackTiles)/(whiteTiles + blackTiles + 1)
    return cornerClosenessHeuristic

def actualMobility(board):
    # Actual mobility is determined by the number of legal moves you have, so we look at the difference between the 
    # number of legal moves of the max player and that of the min player.
    numWhiteMoves = len(getValidMoves(board, WHITE_TILE))
    numBlackMoves = len(getValidMoves(board, BLACK_TILE))
    return 100*(numWhiteMoves - numBlackMoves)/(numWhiteMoves + numBlackMoves + 1)

def potentialMobility(board):
    """
    Potential mobility is calculated by counting the number of empty spaces next to the opponents' coins.
    We consider different sections of the board separately to make the code easier. 
    Discs on edge squares are not considered as they are often not considered as frontier discs.
    """
    whiteMobility, blackMobility = 0, 0
    # NB x and y are misleading here, they are the opposite of what you would intuitively think. Top left is [0][0]
    # and x increases as you go down the board (goes to the next list) and y increases as you go across.
    for x in range(2,6): # interior square
        for y in range(2,6):
            # Check all 8 adjacent squares for squares in the interior:
            if board[x][y+1] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x][y-1] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x+1][y] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x-1][y] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x+1][y+1] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x-1][y+1] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x+1][y-1] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
            if board[x-1][y-1] == EMPTY_SPACE:
                if board[x][y] == WHITE_TILE:
                    blackMobility += 1
                elif board[x][y] == BLACK_TILE:
                    whiteMobility += 1
    
    # rows above and below interior, check left and right for each square (NB confusing [x][y] notation; read above.)
    for y in range(2,6):
        if board[1][y+1] == EMPTY_SPACE:
            if board[1][y] == WHITE_TILE:
                blackMobility += 1
            elif board[1][y] == BLACK_TILE:
                whiteMobility += 1
        if board[1][y-1] == EMPTY_SPACE:
            if board[1][y] == WHITE_TILE:
                blackMobility += 1
            elif board[1][y] == BLACK_TILE:
                whiteMobility += 1
        if board[6][y-1] == EMPTY_SPACE:
            if board[6][y] == WHITE_TILE:
                blackMobility += 1
            elif board[6][y] == BLACK_TILE:
                whiteMobility += 1
        if board[6][y+1] == EMPTY_SPACE:
            if board[6][y] == WHITE_TILE:
                blackMobility += 1
            elif board[6][y] == BLACK_TILE:
                whiteMobility += 1
                
    # columns left and right of interior square, check above and below for each square
    for x in range(2,6):
        if board[x+1][1] == EMPTY_SPACE:
            if board[x][1] == WHITE_TILE:
                blackMobility += 1
            elif board[x][1] == BLACK_TILE:
                whiteMobility += 1
        if board[x-1][1] == EMPTY_SPACE:
            if board[x][1] == WHITE_TILE:
                blackMobility += 1
            elif board[x][1] == BLACK_TILE:
                whiteMobility += 1
        if board[x+1][6] == EMPTY_SPACE:
            if board[x][6] == WHITE_TILE:
                blackMobility += 1
            elif board[x][6] == BLACK_TILE:
                whiteMobility += 1
        if board[x-1][6] == EMPTY_SPACE:
            if board[x][6] == WHITE_TILE:
                blackMobility += 1
            elif board[x][6] == BLACK_TILE:
                whiteMobility += 1
                
    pMobility = 100*(whiteMobility - blackMobility)/(whiteMobility + blackMobility + 1) 
    return pMobility

def discDifference(board):
    # Disc difference or disc parity heuristic. Very important in end game but not so much otherwise.
    scores = getScoreOfBoard(board)
    whiteCount = scores['WHITE_TILE']
    blackCount = scores['BLACK_TILE']
    return 100*(whiteCount - blackCount)/(blackCount + whiteCount + 1)

def stability(board):
    """
    Measures how easily our discs can be flanked. Stable discs cannot be flanked, semi-stable cannot be immediately
    flanked, unstable discs can be flanked immediately. We only look at stable discs in this function.
    Finding all stable discs is difficult, but we can start from corners and look for stable discs from there. Corner
    discs are always stable, and so those adjacent also become stable.
    So this function finds only a lower bound on the number of stable discs; just those that are stable due to corners.
    """
    whiteStableDiscs, blackStableDiscs = 0, 0
    
    # From top left corner, iterate horizontally first
    # Have to make two loops for each colour otherwise could get error e.g. if entire first column is black and second 
    # columns starts with white tile.
    for y in range(8):
        if board[0][y] == WHITE_TILE:
            # iterate vertically
            for x in range(8):
                # if there is a white disc on this square and it is not in the set of stable discs, add it to the set
                if board[x][y] == WHITE_TILE: # this counts corners as stable discs but think this is fine. Actually its
                    # necessary to find stable discs in adjacent columns, i.e. not in the first column we check.
                    whiteStableDiscs += 1
                # if we come across a disc of the opposite colour, stable region ends so break
                else:
                    break
        else: # this loop is only for white tiles so that we avoid errors.
            break
                    
    for y in range(8):
        if board[0][y] == BLACK_TILE:
            for x in range(8):
                if board[x][y] == BLACK_TILE:
                    blackStableDiscs += 1
                else:
                    break
        else:
            break
            
    # from top right corner, iterate horizontally (always horizontally first):
    for y in range(7, -1, -1):
        if board[0][y] == WHITE_TILE:
            for x in range(8):
                if board[x][y] == WHITE_TILE:
                    whiteStableDiscs += 1
                else:
                    break
        else:
            break
    for y in range(7, -1, -1):
        if board[0][y] == BLACK_TILE:
            for x in range(8):
                if board[x][y] == BLACK_TILE:
                    blackStableDiscs += 1
                else:
                    break
        else:
            break
            
    # from bottom left corner:
    for y in range(8):
        if board[7][y] == WHITE_TILE:
            for x in range(7, -1, -1):
                if board[x][y] == WHITE_TILE:
                    whiteStableDiscs += 1
                else:
                    break
        else:
            break
    for y in range(8):
        if board[7][y] == BLACK_TILE:
            for x in range(7, -1, -1):
                if board[x][y] == BLACK_TILE:
                    blackStableDiscs += 1
                else:
                    break
        else:
            break
            
    # from bottom right corner:
    for y in range(7, -1, -1):
        if board[7][y] == WHITE_TILE:
            for x in range(7, -1, -1):
                if board[x][y] == WHITE_TILE:
                    whiteStableDiscs += 1
                else:
                    break
        else:
            break
    for y in range(7, -1, -1): # iterate horizontally to the left
        if board[7][y] == BLACK_TILE:
            for x in range(7, -1, -1):
                # iterate vertically upwards
                if board[x][y] == BLACK_TILE:
                    blackStableDiscs += 1
                else:
                    break
        else:
            break
            
    return 100*(whiteStableDiscs - blackStableDiscs)/(whiteStableDiscs + blackStableDiscs + 1)

def evaluation2(board):
    # generic evaluation function for use at all stages of the game (not optimal)
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)
    
    # weights based off both githubs
    return 800*CO + 400*CC + 20*AM + 20*PM + 10*DD + 500*S

def evaluation3(board):
    # eval function which returns different evaluations for early, mid, and late game.
    scores = getScoreOfBoard(board)
    numTiles = scores['WHITE_TILE'] + scores['BLACK_TILE']
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)
    # Think about the heuristics; CO, CC and S will reduce to 0 on most board states as they involve corners.
    if numTiles <= 20: # early game
        return 1000*CO + 1000*CC + 20*AM + 10*PM + 1000*S
    elif numTiles <= 58: # used to be 54
        return 1000*CO + 1000*CC + 10*AM + 5*PM + 1000*S + 5*DD
    else:
        return 1000*CO + 1000*CC + 1000*S + 500*DD
    
def evaluation4(board):
    """
    This evaluation function is based on the results found in "An Analysis of Heuristics in Othello". 
    """
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)
    
    return 15*CO + 15*CC + 2.5*AM + 2.5*PM + 25*S + 25*DD

def evaluation5(board):
    """
    An eval function with corner closeness to be compared with one without it.
    """
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)
    
    return 30*CO + 30*CC + 2.5*AM + 2.5*PM + 25*S + 25*DD

def evaluation6(board):
    """
    Corner closeness is omitted to test its importance. 
    """
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)
    
    return 30*CO + 2.5*AM + 2.5*PM + 25*S + 25*DD

def evaluation7(board):
    # eval function which returns different evaluations for early, mid, and late game - different take on evaluation3.
    scores = getScoreOfBoard(board)
    numTiles = scores['WHITE_TILE'] + scores['BLACK_TILE']
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)

    if numTiles <= 20: # early game
        return 1000*CO + 1000*CC + 20*AM + 20*PM + 1000*S
    elif numTiles <= 54:
        return 1000*CO + 1000*CC + 10*AM + 10*PM + 1000*S + 5*DD
    elif numTiles <= 58:
        return 1000*CO + 1000*CC + 1000*S + 500*DD
    else:
        return DD
    
def evaluation8(board):
    # eval function which returns different evaluations for mid and late game.
    scores = getScoreOfBoard(board)
    numTiles = scores['WHITE_TILE'] + scores['BLACK_TILE']
    CO = cornerOccupancy(board)
    CC = cornerCloseness(board)
    AM = actualMobility(board)
    PM = potentialMobility(board)
    DD = discDifference(board)
    S = stability(board)

    if numTiles <= 54:
        return 1000*CO + 1000*CC + 20*AM + 6*PM + 4*DD + 1000*S
    else:
        return 1000*CO + 1000*CC + 1000*S + 20*AM + 6*PM + 20*DD