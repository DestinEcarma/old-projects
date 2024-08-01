import pygame as py
import ChessEngine, SmartAi

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
COLORS = [py.Color("white"), py.Color("gray")]

PLAYER_ONE = True
PLAYER_TWO = True

MAX_FPS = 15

IMAGES = {}

def loadImages():
    pieces = {
        "B": "wB",
        "K": "wK",
        "N": "wN",
        "P": "wP",
        "Q": "wQ",
        "R": "wR",
        "b": "bB",
        "k": "bK",
        "n": "bN",
        "p": "bP",
        "q": "bQ",
        "r": "bR"
    }

    for char in pieces:
        piece = pieces[char]

        IMAGES[char] = py.transform.scale(py.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    py.init()
    loadImages()

    gameState = ChessEngine.GameState()

    screen = py.display.set_mode((WIDTH, HEIGHT))
    screen.fill(py.Color("white"))

    clock = py.time.Clock() 
    validMoves = gameState.getValidMoves()

    gameOver = False
    moveMade = False
    animate = False
    running = True
    sqSelected = ()
    playerClicks = [] 

    while running:
        humanTurn = (gameState.whiteToMove and PLAYER_ONE) or (not gameState.whiteToMove and PLAYER_TWO)
        text = None

        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key == py.K_z:
                    gameState.undoMove()

                    if not PLAYER_ONE or not PLAYER_TWO:
                        gameState.undoMove()
                    
                    moveMade = True
                    gameOver = False

                if event.key == py.K_r:
                    gameState = ChessEngine.GameState()
                    validMoves = gameState.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False

                if event.key == py.K_t:
                    SmartAi.PerftTest(gameState, validMoves)
            elif event.type == py.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = py.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) >= 2 and humanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gameState.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if validMoves[i].isPawnPromotion:
                                    promotion = input("Promote to Q, R, B or N:")
                                    validMoves[i].promotionType = str.upper(promotion) if gameState.whiteToMove else str.lower(promotion)

                                gameState.makeMove(validMoves[i])

                                sqSelected = ()
                                playerClicks = []

                                moveMade = True

                        if not moveMade:
                            playerClicks = [sqSelected]

        if moveMade:
            moveMade = False

            validMoves = gameState.getValidMoves()

        if gameState.checkmate:
            gameOver = True

            if gameState.whiteToMove:
                text = "Black wins by checkmate!"
            else:
                text = "White wins by checkmate!"
        elif gameState.stalemate:
            gameOver = True
            text = "Stalemate!"
        else:
            gameOver = False

        drawGameState(screen, gameState, validMoves, sqSelected, text)

        clock.tick(MAX_FPS)
        py.display.flip()

def drawGameState(screen, gameState, validMoves, sqSelected, text):
    drawBoard(screen)
    highlightSquares(screen, gameState, validMoves, sqSelected)

    drawPieces(screen, gameState.board)

    if text != None:
        drawWinningText(screen, text)

def drawBoard(screen):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = COLORS[((row + col) % 2)]
            py.draw.rect(screen, color, py.Rect((col * SQ_SIZE), (row * SQ_SIZE), SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gameState, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected

        selectedPiece = gameState.board[row][col]

        if selectedPiece != "-":
            if (gameState.whiteToMove and str.upper(selectedPiece) == selectedPiece) or (not gameState.whiteToMove and str.lower(selectedPiece) == selectedPiece):
                surface = py.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(75)
                surface.fill(py.Color("blue"))
                screen.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))

                surface.fill(py.Color("yellow"))

                for move in validMoves:
                    if move.startRow == row and move.startCol == col:
                        screen.blit(surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]

            if piece != "-":
                screen.blit(IMAGES[piece], py.Rect((col * SQ_SIZE), (row * SQ_SIZE), SQ_SIZE, SQ_SIZE))

def drawWinningText(screen, text):
    font = py.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, py.Color("gray"))
    textLocation = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, py.Color("black"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()