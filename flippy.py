# Flippy (an Othello or Reversi clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Based on the "reversi.py" code that originally appeared in "Invent
# Your Own Computer Games with Python", chapter 15:
#   http://inventwithpython.com/chapter15.html

import random, sys, pygame, time
from pygame.locals import *
from simple_agents import getDynamicRoxanneMovev3, getRoxanneMove
from board_functions import *
from minimax import minimaxMove, evaluation3
from mcts import MCTS

FPS = 10 # frames per second to update the screen
WINDOWWIDTH = 640 # width of the program's window, in pixels
WINDOWHEIGHT = 480 # height in pixels
SPACESIZE = 50 # width & height of each space on the board, in pixels
BOARDWIDTH = 8 # how many columns of spaces on the game board
BOARDHEIGHT = 8 # how many rows of spaces on the game board
WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value
HINT_TILE = 'HINT_TILE' # an arbitrary but unique value
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

# Amount of space on the left & right side (XMARGIN) or above and below
# (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#              R    G    B
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN


def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Flippy')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    # Set up the background image.
    boardImage = pygame.image.load('flippyboard.png')
    # Use smoothscale() to stretch the board image to fit the entire board:
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
    boardImageRect = boardImage.get_rect()
    boardImageRect.topleft = (XMARGIN, YMARGIN)
    BGIMAGE = pygame.image.load('flippybackground.png')
    # Use smoothscale() to stretch the background image to fit the entire window:
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    BGIMAGE.blit(boardImage, boardImageRect)

    # Run the main game.
    while True:
        if runGame() == False:
            break


def runGame():
    # Plays a single game of reversi each time this function is called.

    # Reset the board and game.
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    turn = random.choice(['computer', 'player'])

    # Draw the starting board and ask the player what color they want.
    drawBoard(mainBoard)
    playerTile, computerTile = enterPlayerTile()

    # Make the Surface and Rect objects for the "New Game" and "Hints" buttons
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR2)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)
    hintsSurf = FONT.render('Hints', True, TEXTCOLOR, TEXTBGCOLOR2)
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (WINDOWWIDTH - 8, 40)

    while True: # main game loop
        # Keep looping for player and computer's turns.
        if turn == 'player':
            # Player's turn:
            if getValidMoves(mainBoard, playerTile) == []:
                # If it's the player's turn but they
                # can't move, then end the game.
                break
            movexy = None
            while movexy == None:
                # Keep looping until the player clicks on a valid space.

                # Determine which board data structure to use for display.
                if showHints:
                    boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                else:
                    boardToDraw = mainBoard

                checkForQuit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        # Handle mouse click events
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint( (mousex, mousey) ):
                            # Start a new game
                            return True
                        elif hintsRect.collidepoint( (mousex, mousey) ):
                            # Toggle hints mode
                            showHints = not showHints
                        # movexy is set to a two-item tuple XY coordinate, or None value
                        movexy = getSpaceClicked(mousex, mousey)
                        if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                            movexy = None

                # Draw the game board.
                drawBoard(boardToDraw)
                drawInfo(boardToDraw, playerTile, computerTile, turn)

                # Draw the "New Game" and "Hints" buttons.
                DISPLAYSURF.blit(newGameSurf, newGameRect)
                DISPLAYSURF.blit(hintsSurf, hintsRect)

                MAINCLOCK.tick(FPS)
                pygame.display.update()

            # Make the move and end the turn.
            makeMove(mainBoard, playerTile, movexy[0], movexy[1], True)
            if getValidMoves(mainBoard, computerTile) != []:
                # Only set for the computer's turn if it can make a move.
                turn = 'computer'

        else:
            # Computer's turn:
            if getValidMoves(mainBoard, computerTile) == []:
                # If it was set to be the computer's turn but
                # they can't move, then end the game.
                break

            # Draw the board.
            drawBoard(mainBoard)
            drawInfo(mainBoard, playerTile, computerTile, turn)

            # Draw the "New Game" and "Hints" buttons.
            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(hintsSurf, hintsRect)

            # Make it look like the computer is thinking by pausing a bit.
            pauseUntil = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pauseUntil:
                pygame.display.update()

            # Make the move and end the turn.
            opponent = getOpponent()
            x, y = getOpponentMove(opponent, mainBoard, computerTile)
            makeMove(mainBoard, computerTile, x, y, True)
            if getValidMoves(mainBoard, playerTile) != []:
                # Only set for the player's turn if they can make a move.
                turn = 'player'

    # Display the final score.
    drawBoard(mainBoard)
    scores = getScoreOfBoard(mainBoard)

    # Determine the text of the message to display.
    if scores[playerTile] > scores[computerTile]:
        text = 'You beat the computer by %s points! Congratulations!' % \
               (scores[playerTile] - scores[computerTile])
    elif scores[playerTile] < scores[computerTile]:
        text = 'You lost. The computer beat you by %s points.' % \
               (scores[computerTile] - scores[playerTile])
    else:
        text = 'The game was a tie!'

    textSurf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(textSurf, textRect)

    # Display the "Play again?" text with Yes and No buttons.
    text2Surf = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

    # Make "Yes" button.
    yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

    # Make "No" button.
    noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
    noRect = noSurf.get_rect()
    noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)

    while True:
        # Process events until the user clicks on Yes or No.
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yesRect.collidepoint( (mousex, mousey) ):
                    return True
                elif noRect.collidepoint( (mousex, mousey) ):
                    return False
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(text2Surf, text2Rect)
        DISPLAYSURF.blit(yesSurf, yesRect)
        DISPLAYSURF.blit(noSurf, noRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def getOpponent():
    '''
    Identifies the opponent from the command line arguments.
    '''
    if len(sys.argv) == 1: # no opponent specified; use default getComputerMove
        opponent = 'getComputerMove'
        return opponent
    elif len(sys.argv) == 2: # opponent is a simple agent
        opponent = sys.argv[1]
        return opponent
    elif sys.argv[1].lower() == 'minimax':
        opponentDetails = sys.argv[1:]
        return opponentDetails
    elif sys.argv[1].lower() == 'mcts':
        opponentDetails = sys.argv[1:]
        return opponentDetails
    
def getOpponentMove(opponent, board, tile):
    '''
    Gets the opponent move given the opponent.
    '''
    # the dirty code goes here
    if opponent == 'getComputerMove':
        return getComputerMove(board, tile)
    elif opponent == 'Roxanne3':
        return getDynamicRoxanneMovev3(board, tile)
    elif opponent == 'Roxanne':
        return getRoxanneMove(board, tile)
    elif opponent[0] == 'minimax':
        return minimaxMove(board, int(opponent[1]), tile, alpha=float("-inf"), beta=float("inf"), evaluation=evaluation3)
    elif opponent[0] == 'mcts':
        return MCTS(board, tile, int(opponent[1]))
    else:
        raise Exception("Invalid opponent chosen. Choose opponent from the following list: '' (ComputerMove), 'Roxanne3', 'Roxanne', 'minimax', 'mcts'. Type the opponent as a command line argument. When using 'minimax', specify the depth as the next command line argument. When using 'mcts' specify the number of simulations as the next command line argument. E.g. py main.py minimax 1")

def translateBoardToPixelCoord(x, y):
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)


def animateTileChange(tilesToFlip, tileColor, additionalTile):
    # Draw the additional tile that was just laid down. (Otherwise we'd
    # have to completely redraw the board & the board info.)
    if tileColor == WHITE_TILE:
        additionalTileColor = WHITE
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
    pygame.display.update()

    for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0

        if tileColor == WHITE_TILE:
            color = tuple([rgbValues] * 3) # rgbValues goes from 0 to 255
        elif tileColor == BLACK_TILE:
            color = tuple([255 - rgbValues] * 3) # rgbValues goes from 255 to 0

        for x, y in tilesToFlip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        checkForQuit()


def drawBoard(board):
    # Draw background of board.
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    # Draw grid lines of the board.
    for x in range(BOARDWIDTH + 1):
        # Draw the horizontal lines.
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        # Draw the vertical lines.
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    # Draw the black & white tiles or hint spots.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)
            if board[x][y] == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))


def getSpaceClicked(mousex, mousey):
    # Return a tuple of two integers of the board space coordinates where
    # the mouse was clicked. (Or returns None not in any space.)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > x * SPACESIZE + XMARGIN and \
               mousex < (x + 1) * SPACESIZE + XMARGIN and \
               mousey > y * SPACESIZE + YMARGIN and \
               mousey < (y + 1) * SPACESIZE + YMARGIN:
                return (x, y)
    return None


def drawInfo(board, playerTile, computerTile, turn):
    # Draws scores and whose turn it is at the bottom of the screen.
    scores = getScoreOfBoard(board)
    scoreSurf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[playerTile]), str(scores[computerTile]), turn.title()), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def enterPlayerTile():
    # Draws the text and handles the mouse click events for letting
    # the player choose which color they want to be.  Returns
    # [WHITE_TILE, BLACK_TILE] if the player chooses to be White,
    # [BLACK_TILE, WHITE_TILE] if Black.

    # Create the text.
    textSurf = FONT.render('Do you want to be white or black?', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    xSurf = BIGFONT.render('White', True, TEXTCOLOR, TEXTBGCOLOR1)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)

    oSurf = BIGFONT.render('Black', True, TEXTCOLOR, TEXTBGCOLOR1)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)

    while True:
        # Keep looping until the player has clicked on a color.
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return [WHITE_TILE, BLACK_TILE]
                elif oRect.collidepoint( (mousex, mousey) ):
                    return [BLACK_TILE, WHITE_TILE]

        # Draw the screen.
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def makeMove(board, tile, xstart, ystart, realMove=False): # Need this function in flippy.py
    # Place the tile on the board at xstart, ystart, and flip tiles
    # Returns False if this is an invalid move, True if it is valid.
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(tilesToFlip, tile, (xstart, ystart))

    for x, y in tilesToFlip:
        board[x][y] = tile
    return True

def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main() 