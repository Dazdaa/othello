# Contains all the basic board functions which will need to be used in basically all other files.
# These functions are purely for manipulating the board, unlike the functions in flippy which are used to run the game using pygame.

import copy, random

BOARDWIDTH = 8 # how many columns of spaces on the game board
BOARDHEIGHT = 8 # how many rows of spaces on the game board
WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value
HINT_TILE = 'HINT_TILE' # an arbitrary but unique value

def resetBoard(board):
    # Blanks out the board it is passed, and sets up starting tiles.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE

    # Add starting pieces to the center
    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE


def getNewBoard():
    # Creates a brand new, empty board data structure.
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)

    return board

def isValidMove(board, tile, xstart, ystart):
    # Returns False if the player's move is invalid. If it is a valid
    # move, returns a list of spaces of the captured pieces.
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = tile # temporarily set the tile on the board.

    if tile == WHITE_TILE:
        otherTile = BLACK_TILE
    else:
        otherTile = WHITE_TILE

    tilesToFlip = []
    # check each of the eight directions:
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            # The piece belongs to the other player next to our piece.
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break # break out of while loop, continue in for loop
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                # There are pieces to flip over. Go in the reverse
                # direction until we reach the original space, noting all
                # the tiles along the way.
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = EMPTY_SPACE # make space empty
    if len(tilesToFlip) == 0: # If no tiles flipped, this move is invalid
        return False
    return tilesToFlip

def isOnBoard(x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT

def getBoardWithValidMoves(board, tile):
    # Returns a new board with hint markings.
    dupeBoard = copy.deepcopy(board)

    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = HINT_TILE
    return dupeBoard

def getValidMoves(board, tile):
    # Returns a list of (x,y) tuples of all valid moves.
    validMoves = []

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves

def getScoreOfBoard(board):
    # Determine the score by counting the tiles.
    xscore = 0
    oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITE_TILE:
                xscore += 1
            if board[x][y] == BLACK_TILE:
                oscore += 1
    return {WHITE_TILE:xscore, BLACK_TILE:oscore}

def makeMove(board, tile, xstart, ystart):
    # Place the tile on the board at xstart, ystart, and flip tiles
    # Returns False if this is an invalid move, True if it is valid.
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    for x, y in tilesToFlip:
        board[x][y] = tile
    return True

def isOnCorner(x, y):
    # Returns True if the position is in one of the four corners.
    return (x == 0 and y == 0) or \
           (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or \
           (x == BOARDWIDTH and y == BOARDHEIGHT)

def getComputerMove(board, computerTile):
    # Given a board and the computer's tile, determine where to
    # move and return that move as a [x, y] list.
    # This agent has the following strategy: Capture a corner if possible. If not, play the move which captures the
    # most discs. So corner + max disc strat.
    possibleMoves = getValidMoves(board, computerTile)

    # randomize the order of the possible moves
    random.shuffle(possibleMoves)

    # always go for a corner if available.
    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]

    # Go through all possible moves and remember the best scoring move
    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove