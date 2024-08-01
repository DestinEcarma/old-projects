import pygame as py
import ChessEngine, SmartAi

import random

from multiprocessing import Process, Queue

py.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
COLORS = [py.Color("white"), py.Color("gray")]
TEXT_COLORS = [py.Color("gray"), py.Color("white")]
COLSTOFILES = ChessEngine.Move.colsToFiles
ROWSTORANKS = ChessEngine.Move.rowsToRanks

def generateRandom():
    pass

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
    lastMove = ()

    playerOne = True
    playerTwo = True

    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    generatedHash = generateDataTable()

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        text = None

        for e in py.event.get():
            if e.type == py.QUIT:
                if AIThinking:
                    moveFinderProcess.terminate()
                    AIThinking = False

                running = False
            elif e.type == py.KEYDOWN:
                if e.key == py.K_z:
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False

                    gs.undoMove()
                    
                    if not playerOne or not playerTwo:
                        gs.undoMove()
                        
                    moveMade = True
                    gameOver = False

                    if len(lastMove) > 2:
                        move = gs.moveLog[-1]
                        lastMove = ((move.startRow, move.startCol), (move.endRow, move.endCol))
                    else:
                        lastMove = ()
                    moveUndone = True

                if e.key == py.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    lastMove = ()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    moveUndone = True
            elif e.type == py.MOUSEBUTTONDOWN:
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
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                print(move.getChessNotation())
                                gs.makeMove(validMoves[i], isHuman=True)

                                startRow = validMoves[i].startRow
                                startCol = validMoves[i].startCol
                                endRow = validMoves[i].endRow
                                endCol = validMoves[i].endCol

                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                                lastMove = ((startRow, startCol), (endRow, endCol))

                        if not moveMade:
                            playerClicks = [sqSelected]

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True 
                returnQueue = Queue()
                moveFinderProcess = Process(target=SmartAi.findBestMove, args=(gs, validMoves, generatedHash, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIThinking = False
                data = returnQueue.get()
                AIMove = data[0]
                hash = data[1]

                generatedHash.dataTable = hash

                gs.makeMove(AIMove)
                #print(AIMove.getChessNotation())

                moveMade = True
                animate = True
                lastMove = ((AIMove.startRow, AIMove.startCol), (AIMove.endRow, AIMove.endCol))
 
        if moveMade:
            if animate:
                animate = False
                animateMove(screen, gs.moveLog[-1], gs.board, clock, lastMove)

            validMoves = gs.getValidMoves()

            moveMade = False
            moveUndone = False

        if gs.checkmate:
            gameOver = True

            if gs.whiteToMove:
                text = "Black wins by checkmate!"
            else:
                text = "White wins by checkmate!"
        elif gs.stalemate:
            gameOver = True
            text = "Stalemate!"
        else:
            gameOver = False

        drawGameState(screen, gs, validMoves, sqSelected, lastMove, text)

        clock.tick(MAX_FPS)
        py.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected, lastMove, text):
    drawBoard(screen)
    hightlightLastMove(screen, lastMove)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

    if not text is None:
        drawText(screen, text)

def drawText(screen, text):
    font = py.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, py.Color("gray"))
    textLocation = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, py.Color("black"))
    screen.blit(textObject, textLocation.move(2, 2))

def hightlightLastMove(screen, lastMove):
    if lastMove != ():
        s = py.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(75)
        s.fill(py.Color("red"))
        screen.blit(s, (lastMove[0][1] * SQ_SIZE, lastMove[0][0] * SQ_SIZE))
        s.fill(py.Color("red"))
        screen.blit(s, (lastMove[1][1] * SQ_SIZE, lastMove[1][0] * SQ_SIZE))

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

def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            py.draw.rect(screen, color, py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))

            if c == 0:
                text = ROWSTORANKS[r]
                font = py.font.SysFont("Helvitca", 24, True, False)
                textObject = font.render(text, 0, TEXT_COLORS[((r + c) % 2)])
                screen.blit(textObject, (c * SQ_SIZE, r * SQ_SIZE))
            if r == 7:
                text = COLSTOFILES[c]
                font = py.font.SysFont("Helvitca", 24, True, False)
                textObject = font.render(text, 0, TEXT_COLORS[((r + c) % 2)])
                textLocation = py.Rect(0, 0, SQ_SIZE, SQ_SIZE).move((c * SQ_SIZE), (r * SQ_SIZE))
                screen.blit(textObject, textLocation.move(SQ_SIZE - textObject.get_width(), SQ_SIZE - textObject.get_height()))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]

            if piece != "--":
                screen.blit(IMAGES[piece], py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))

def createSquare(endRow, endCol):
    color = COLORS[(endRow + endCol) % 2]
    endSquare = py.Rect((endCol * SQ_SIZE), (endRow * SQ_SIZE), SQ_SIZE, SQ_SIZE)

    return color, endSquare

def addRanks(screen, endRow, endCol, text):
    font = py.font.SysFont("Helvitca", 24, True, False)
    textObject = font.render(text, 0, TEXT_COLORS[((endRow + endCol) % 2)])
    textLocation = py.Rect(0, 0, SQ_SIZE, SQ_SIZE).move((endCol * SQ_SIZE), (endRow * SQ_SIZE))

    if endRow == 7:
        screen.blit(textObject, textLocation.move(SQ_SIZE - textObject.get_width(), SQ_SIZE - textObject.get_height()))
    if endCol == 0:
        screen.blit(textObject, (endCol * SQ_SIZE, endRow * SQ_SIZE))

def animateMove(screen, move, board, clock, lastMove):
    startRow = move.startRow
    startCol = move.startCol
    endRow = move.endRow
    endCol = move.endCol
    moveAmount = 0 

    if move.isCastleMove:
        if endCol - startCol == 2:
            moveAmount = 1
            rookLocation = -1
        else:
            moveAmount = -2
            rookLocation = 1
        
        castleDC = (endCol + rookLocation) - (endCol + moveAmount)

    dR = endRow - startRow
    dC = endCol - startCol

    castleStartCol = (endCol + moveAmount)

    framesPerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        drawBoard(screen)
        drawPieces(screen, board)
        hightlightLastMove(screen, lastMove)

        color, endSquare = createSquare(endRow, endCol)
        py.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enpassantEndRow = endRow + 1 if move.pieceMoved[0] == "w" else endRow - 1

                endSquare = py.Rect((endCol * SQ_SIZE), ((enpassantEndRow) * SQ_SIZE), SQ_SIZE, SQ_SIZE)

                if endCol == 0:
                    addRanks(screen, (enpassantEndRow), endCol, str(ROWSTORANKS[enpassantEndRow]))

                screen.blit(IMAGES[move.pieceCaptured], endSquare)
            else:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        elif move.isCastleMove:
            r, c = ((startRow + dR * frame/frameCount, castleStartCol + castleDC * frame/frameCount))
            castleEndCol = endCol - 1 if endCol - startCol == 2 else endCol + 1
            
            color, endSquare = createSquare(endRow, castleEndCol)
            py.draw.rect(screen, color, endSquare)

            if endRow == 7:
                addRanks(screen, endRow, castleEndCol, COLSTOFILES[castleEndCol])

            screen.blit(IMAGES[move.pieceMoved[0] + "R"], py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))
        
        if endCol == 0:
            addRanks(screen, endRow, endCol, str(ROWSTORANKS[endRow]))

        if endRow == 7:
            addRanks(screen, endRow, endCol, COLSTOFILES[endCol])

        r, c = ((startRow + dR * frame/frameCount, startCol + dC * frame/frameCount))
        
        screen.blit(IMAGES[move.pieceMoved], py.Rect((c * SQ_SIZE), (r * SQ_SIZE), SQ_SIZE, SQ_SIZE))
        py.display.flip()
        clock.tick(60)

class generateDataTable():
    def __init__(self):
        self.dataTable = {}
        self.zobTable = [[[random.randint(1, 2 ** 64 - 1) for r in range(12)] for c in range(8)] for k in range(8)]

    def indexing(self, piece):
        if piece[0] == "w":
            piece = piece[1]

            if (piece == 'P'):
                return 0
            elif (piece == 'N'):
                return 1
            elif (piece == 'B'):
                return 2
            elif (piece == 'R'):
                return 3
            elif (piece == 'Q'):
                return 4
            elif (piece == 'K'):
                return 5
        elif piece[0] == "b":
            piece = piece[1]

            if (piece == 'P'):
                return 6
            elif (piece == 'N'):
                return 7
            elif (piece== 'B'):
                return 8
            elif (piece == 'R'):
                return 9
            elif (piece == 'Q'):
                return 10
            elif (piece == 'K'):
                return 11
        else:
            return -1

    def zobristHash(self, board):
        hash = 0
        
        for r in range(len(board)):
            for c in range(len(board[r])):
                if board[r][c] != "--":
                    piece = self.indexing(board[r][c])

                    hash ^= self.zobTable[r][c][piece]

        return hash

if __name__ == "__main__":
    main()