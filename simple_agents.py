from flippy import getValidMoves, makeMove, getScoreOfBoard
import random, copy

WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value

def getRandomComputerMove(board, computerTile):
    # This agent plays a completely random computer move.
    possibleMoves = getValidMoves(board, computerTile)
    return random.choice(possibleMoves)

# Priority of moves according to Roxanne method
RoxanneMatrix = [[1,5,3,3,3,3,5,1],
                [5,5,4,4,4,4,5,5],
                [3,4,2,2,2,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,2,2,2,4,3],
                [5,5,4,4,4,4,5,5],
                [1,5,3,3,3,3,5,1]]

def getRoxanneMove(board, computerTile):
    # This agent plays the highest priority move according to the Roxanne method.
    possibleMoves = getValidMoves(board, computerTile)
    
    highestPriorityIndex = 9
    # Find the lowest number in the Roxanne matrix available on this move:
    for x, y in possibleMoves:
        if RoxanneMatrix[x][y] < highestPriorityIndex:
            highestPriorityIndex = RoxanneMatrix[x][y]
    
    RoxanneMoves = []
    # Get all the moves with the highest priority and randomly choose one:
    for x, y in possibleMoves:
        if RoxanneMatrix[x][y] == highestPriorityIndex:
            RoxanneMoves.append([x, y])
    
    return random.choice(RoxanneMoves)

def getDynamicRoxanneMovev1(board, tile):
    # This agent changes the Roxanne priority order when corner squares get captured by us.
    originalRoxanneMatrix = [[1,5,3,3,3,3,5,1],
                [5,5,4,4,4,4,5,5],
                [3,4,2,2,2,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,2,2,2,4,3],
                [5,5,4,4,4,4,5,5],
                [1,5,3,3,3,3,5,1]]
    
    if board[0][0] == tile:
        originalRoxanneMatrix[0][1] = 2
        originalRoxanneMatrix[1][1] = 2
        originalRoxanneMatrix[1][0] = 2
    if board[7][0] == tile:
        originalRoxanneMatrix[6][0] = 2
        originalRoxanneMatrix[7][1] = 2
        originalRoxanneMatrix[6][1] = 2
    if board[0][7] == tile:
        originalRoxanneMatrix[1][7] = 2
        originalRoxanneMatrix[0][6] = 2
        originalRoxanneMatrix[1][6] = 2
    if board[7][7] == tile:
        originalRoxanneMatrix[7][6] = 2
        originalRoxanneMatrix[6][7] = 2
        originalRoxanneMatrix[6][6] = 2
    
    possibleMoves = getValidMoves(board, tile)
    highestPriorityIndex = 9
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] < highestPriorityIndex:
            highestPriorityIndex = originalRoxanneMatrix[x][y]
            
    RoxanneMoves = []
    # Get all the moves with the highest priority and randomly choose one:
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] == highestPriorityIndex:
            RoxanneMoves.append([x, y])
            
    return random.choice(RoxanneMoves)

def getDynamicRoxanneMovev2(board, tile):
    # Places a lower priority than v1 on capturing squares adjacent to corner squares which have been captured by us.
    originalRoxanneMatrix = [[1,5,3,3,3,3,5,1],
                [5,5,4,4,4,4,5,5],
                [3,4,2,2,2,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,2,2,2,4,3],
                [5,5,4,4,4,4,5,5],
                [1,5,3,3,3,3,5,1]]
    
    if board[0][0] == tile:
        originalRoxanneMatrix[0][1] = 3
        originalRoxanneMatrix[1][1] = 3
        originalRoxanneMatrix[1][0] = 3
    if board[7][0] == tile:
        originalRoxanneMatrix[6][0] = 3
        originalRoxanneMatrix[7][1] = 3
        originalRoxanneMatrix[6][1] = 3
    if board[0][7] == tile:
        originalRoxanneMatrix[1][7] = 3
        originalRoxanneMatrix[0][6] = 3
        originalRoxanneMatrix[1][6] = 3
    if board[7][7] == tile:
        originalRoxanneMatrix[7][6] = 3
        originalRoxanneMatrix[6][7] = 3
        originalRoxanneMatrix[6][6] = 3
    
    possibleMoves = getValidMoves(board, tile)
    highestPriorityIndex = 9
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] < highestPriorityIndex:
            highestPriorityIndex = originalRoxanneMatrix[x][y]
            
    RoxanneMoves = []
    # Get all the moves with the highest priority and randomly choose one:
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] == highestPriorityIndex:
            RoxanneMoves.append([x, y])
            
    return random.choice(RoxanneMoves)

def getDynamicRoxanneMovev3(board, tile):
    """
    This agent changes the Roxanne priority order when corner squares get captured by us AND the opponent. It favours 
    capturing squares adjacent to the corners once the corner has been captured by either player.
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
        
    possibleMoves = getValidMoves(board, tile)
    highestPriorityIndex = 9
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] < highestPriorityIndex:
            highestPriorityIndex = originalRoxanneMatrix[x][y]
            
    RoxanneMoves = []
    # Get all the moves with the highest priority and randomly choose one:
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] == highestPriorityIndex:
            RoxanneMoves.append([x, y])
            
    return random.choice(RoxanneMoves)

def getDynamicRoxanneMovev4(board, tile):
    # Similar to v3, except placing a lower priority on capturing squares adjacent to corner squares which have been captured.
    originalRoxanneMatrix = [[1,5,3,3,3,3,5,1],
                [5,5,4,4,4,4,5,5],
                [3,4,2,2,2,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,9,9,2,4,3],
                [3,4,2,2,2,2,4,3],
                [5,5,4,4,4,4,5,5],
                [1,5,3,3,3,3,5,1]]
    
    if board[0][0] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[0][1] = 3
        originalRoxanneMatrix[1][1] = 3
        originalRoxanneMatrix[1][0] = 3 
    if board[7][0] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[6][0] = 3
        originalRoxanneMatrix[7][1] = 3
        originalRoxanneMatrix[6][1] = 3
    if board[0][7] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[1][7] = 3
        originalRoxanneMatrix[0][6] = 3
        originalRoxanneMatrix[1][6] = 3
    if board[7][7] is not 'EMPTY_SPACE':
        originalRoxanneMatrix[7][6] = 3
        originalRoxanneMatrix[6][7] = 3
        originalRoxanneMatrix[6][6] = 3
        
    possibleMoves = getValidMoves(board, tile)
    highestPriorityIndex = 9
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] < highestPriorityIndex:
            highestPriorityIndex = originalRoxanneMatrix[x][y]
            
    RoxanneMoves = []
    # Get all the moves with the highest priority and randomly choose one:
    for x, y in possibleMoves:
        if originalRoxanneMatrix[x][y] == highestPriorityIndex:
            RoxanneMoves.append([x, y])
            
    return random.choice(RoxanneMoves)

def getMinDiscMove(board, computerTile):
    # This agent always plays the move that captures the least discs.
    possibleMoves = getValidMoves(board, computerTile)
    random.shuffle(possibleMoves) # Need to shuffle moves for the below for loop.
    bestScore = 1000 # higher than max possible score of 64
    
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score < bestScore:
            bestMove = [x, y]
            bestScore = score
            
    return bestMove

def getMaxDiscMove(board, computerTile):
    # This agent always plays the move that captures the most discs.
    possibleMoves = getValidMoves(board, computerTile)
    random.shuffle(possibleMoves) # Need to shuffle moves for the below for loop.
    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
            
    return bestMove

def getBestScoreDiffMove(board, computerTile):
    # This agent always plays that maximises the difference between the agents score and the opponents score.
    # This is the same as our initial basic evaluation function for minimax.
    possibleMoves = getValidMoves(board, computerTile)
    random.shuffle(possibleMoves) # Need to shuffle moves for the below for loop.
    bestScore = -1000 
    # Try and make same as basic eval function:
    opponentTile = list(set([BLACK_TILE, WHITE_TILE]) - set([computerTile]))[0]
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        scores = getScoreOfBoard(dupeBoard)
        score = scores[computerTile] - scores[opponentTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
            
    return bestMove