from board_functions import *
from minimax import checkGameOver, declareWinner, minimaxMove, evaluation3
from simple_agents import getRandomComputerMove, getDynamicRoxanneMovev3
import copy, random, math

WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value

# Use classes so that we have a node object for each node in the tree. Each node object keeps track of its child 
# nodes as well as the number of times it has been visited. 
# Think using classes makes the coding easier; each node should have some numerical values assigned to it, and various 
# functions should be performed on nodes.
class Node:
    total_visits = 0
    def __init__(self,board,tile,parent=None,C=1):
        """
        Each node has the following properties.
        """
        self.children = {} # The values are the UCB1 values of the child nodes, the keys are the coordinates of the next
        # move that leads to that child node.
        self.visits = 0
        self.value = 0
        self.board = board
        self.parent = parent
        self.depth = 0 if parent is None else parent.depth + 1 # Depth is the depth of the node in the tree.
        self.tile = tile
        self.C = C

    def is_fully_expanded(self):
        """
        Checks if all of the next possible moves have been added to the tree as child nodes.
        """
        return len(self.children) == len(self.available_actions())

    def available_actions(self):
        """
        Returns all the next possible moves.
        """
        validMoves = getValidMoves(self.board, self.tile)
        if validMoves:
            return getValidMoves(self.board, self.tile)
        else:
            opponentTile = list(set([BLACK_TILE, WHITE_TILE]) - set([str(self.tile)]))[0]
            return getValidMoves(self.board, opponentTile)

    def select(self):
        """
        Returns the child node with the greatest UCB1 value.
        """
        # Child will be of opposite colour so actually want it to be min ucb value I think.
        # Actually depends on what we do in the ucb formula. Can reverse the signs and swap max and min here but its the
        # same.
        return max(self.children.values(), key=lambda x: x.ucb1())


    def expand(self):
        """
        Expands the game tree by creating a child node corresponding to any of the possible moves and then returns it.
        """
        actions = self.available_actions()
        while True:
            # Doesn't matter which move to select; all nodes are initialised with arbitrarily high UCB1 value.
            action = random.sample(actions,1)[0] # Just gets random element from a list.
            if action not in self.children.keys(): # So self.children.keys() should contain coordinates for the next
                # possible moves.
                break
                
        dupeBoard = copy.deepcopy(self.board) # Create duplicated board to pass on to the child node.
        opponentTile = list(set([BLACK_TILE, WHITE_TILE]) - set([str(self.tile)]))[0]
        # Play the new move on the child node, i.e. create the child node:
        makeMove(dupeBoard, self.tile, action[0], action[1])
        child = Node(dupeBoard, opponentTile, self, self.C) # The child node will be of the opposite colour to the parent node.
        self.children[action] = child
        return child

    def back_propagate(self,winner):
        """
        Performs the backpropagation step in MCTS. total_visits is the total number of node visits for across all nodes.
        """
        if winner == 'WHITE' and self.tile == WHITE_TILE:
            self.value += 1 # Reward when we win.
            self.visits += 1
        elif winner == 'WHITE' and self.tile == BLACK_TILE:
            self.visits += 1
            self.value -= 1 # Penalise when we lose.
        elif winner == 'BLACK' and self.tile == WHITE_TILE:
            self.visits += 1
            self.value -= 1
        elif winner == 'BLACK' and self.tile == BLACK_TILE:
            self.value += 1
            self.visits += 1
        else: # award no points in event of draw
            self.visits += 1
            
        Node.total_visits += 1
        if not self.parent is None:
            self.parent.back_propagate(winner)

    def ucb1(self):
        """
        The UCB1 formula which balances exploitation vs. exploration. Returns the UCB1 value of this node.
        """
        # Basically just reverse signs if taking minimum ucb value for child node.
        # Otherwise, first term is negative because child node is of opposite tile so want the child with the most negative
        # value (and there is a negative sign to make that term positive). 
        return -self.value/self.visits + self.C*math.sqrt(2 * math.log(self.parent.visits,math.e) / self.visits)

    def is_end(self):
        """
        Checks if the game is over (if there are any more valid moves).
        """
        gameState = checkGameOver(self.board)
        if gameState is not 'NOBODY':
            return True
        else:
            return False
        
def Playout(board, tile, playout):
    """
    Takes a given board state and plays out the rest of the game according to some playout policy, e.g. a random playout
    policy which just makes random moves for both players until the game ends.
    """
    playoutBoard = copy.deepcopy(board)
    currentTile = tile
    gameState = checkGameOver(playoutBoard)
    
    while gameState is 'NOBODY':
        oppTile = list(set([BLACK_TILE, WHITE_TILE]) - set([str(currentTile)]))[0]
        if getValidMoves(playoutBoard, currentTile):
            if playout == 'DynamicRoxanne3':
                action = getDynamicRoxanneMovev3(playoutBoard, currentTile) # DynamicRoxanne3 playout policy
            elif playout == 'evaluation3':
                action = minimaxMove(playoutBoard, 0, currentTile, float("-inf"), float("inf"), evaluation3)
            elif playout == 'Random':
                action = getRandomComputerMove(playoutBoard, currentTile) # Random playout policy
            else:
                raise Exception("Invalid playout policy selected. Review playout argument.")
            makeMove(playoutBoard, currentTile, action[0], action[1])
            currentTile = list(set([BLACK_TILE, WHITE_TILE]) - set([str(currentTile)]))[0] # Switch tiles for the next move
        elif getValidMoves(playoutBoard, oppTile):
            if playout == 'DynamicRoxanne3':
                action = getDynamicRoxanneMovev3(playoutBoard, oppTile) # DynamicRoxanne3 playout policy
            elif playout == 'evaluation3':
                action = minimaxMove(playoutBoard, 0, oppTile, float("-inf"), float("inf"), evaluation3)
            elif playout == 'Random':
                action = getRandomComputerMove(playoutBoard, oppTile)
            else:
                raise Exception("Invalid playout policy selected. Review playout argument.")
            makeMove(playoutBoard, oppTile, action[0], action[1])
            currentTile = list(set([BLACK_TILE, WHITE_TILE]) - set([str(oppTile)]))[0]

        gameState = checkGameOver(playoutBoard)

    winner = declareWinner(playoutBoard)
    return winner

def MCTS(board, tile, numSimulations, C=4, playout='DynamicRoxanne3'):
    """
    Takes the current board state as the root node of the game tree and then runs the MCTS algorithm. Returns the best 
    move found.
    """
    copyBoard = copy.deepcopy(board)
    rootNode = Node(copyBoard, tile, None, C)
    for i in range(numSimulations):
        node = rootNode # Start at the top of the tree each time, traversing down the tree using UCB1.
        while not node.is_end():
            if node.is_fully_expanded():
                node = node.select() #  no break after this line so that MCTS traverses down the tree
                # so that it can reach the leaf nodes on each iteration.
            else:  # This else statement ensures that we explore all child nodes once before going deeper.
                node = node.expand()
                break
        playoutResult = Playout(node.board, node.tile, playout)
        node.back_propagate(playoutResult)
        
    bestMove = min(rootNode.children, key=lambda x: rootNode.children[x].value)
    return bestMove