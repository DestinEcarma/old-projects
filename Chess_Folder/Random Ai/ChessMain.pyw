import pygame as py
import ChessEngine
import RandomAI

py.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 30
IMAGES = {}
COLORS = [py.Color("white"), py.Color("gray")]

def loadImages():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]

    for piece in pieces:
        IMAGES[piece] = py.transform.scale(py.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():  
    py.init
    loadImages()

    screen = py.display.set_mode((WIDTH, HEIGHT))
    screen.fill(py.Color("white"))

    clock = py.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()

    gameOver = False
    moveMade = False
    animate = False
    running = True
    sqSelected = ()
    playerClicks = []

    playerOne = True  
    playerTwo = False
    
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
            elif e.type == py.KEYDOWN:
                if e.key == py.K_z:
                    gs.undoMove()
                    gs.undoMove()
                    moveMade = True
                if e.key == py.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
            elif e.type == py.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = py.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE 

                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    if len(playerClicks) >= 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                print(move.getChessNotation())

                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []

                        if not moveMade:
                            playerClicks = [sqSelected]

        if not gameOver and not humanTurn:
            AIMove = RandomAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animate = False
                animateMove(screen, gs.moveLog[-1], gs.board, clock)

            validMoves = gs.getValidMoves()
            moveMade = False

        if gs.checkmate:
            gameOver = True

            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate!")
            else:
                drawText(screen, "White wins by checkmate!")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate!")
        else:
            gameOver = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        py.display.flip()

def drawText(screen, text):
    font = py.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, py.Color("gray"))
    textLocation = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, py.Color("black"))
    screen.blit(textObject, textLocation.move(2, 2))
    py.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected

        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            s = py.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(75)
            s.fill(py.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            s.fill(py.Color("yellow"))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            py.draw.rect(screen, color, py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]

            if piece != "--":
                screen.blit(IMAGES[piece], py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))

def animateMove(screen, move, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount))

        drawBoard(screen)
        drawPieces(screen, board)

        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = py.Rect((move.endCol * SQ_SIZE), (move.endRow * SQ_SIZE), SQ_SIZE, SQ_SIZE)
        py.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                if move.pieceMoved[0] == "w":
                    moveAmount = 1
                elif move.pieceMoved[0] == "b":
                    moveAmount = -1

                color = COLORS[((move.endRow + moveAmount)+ move.endCol) % 2]
                endSquare = py.Rect((move.endCol * SQ_SIZE), ((move.endRow + moveAmount) * SQ_SIZE), SQ_SIZE, SQ_SIZE)
                py.draw.rect(screen, color, endSquare)

                screen.blit(IMAGES[move.pieceCaptured], endSquare)
            else:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        
        screen.blit(IMAGES[move.pieceMoved], py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))
        py.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()