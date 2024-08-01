import random

pieceScore = {
    "K": 0,
    "P": 1,
    "B": 3,
    "N": 3,
    "R": 5,
    "Q": 10
}

CHECKMATE = 1000
STALEMATE = 0

def look1MoveAhead(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1

    maxScore = -CHECKMATE
    bestMove = None

    for playerMove in validMoves:
        gs.makeMove(playerMove, isHuman=False)
        score = turnMultiplier * scoreMaterial(gs.board)

        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = 0

        if score > maxScore and not gs.whiteToMove:
            maxScore = score
            bestMove = playerMove
        elif score > maxScore and gs.whiteToMove:
            score = maxScore
            bestMove = playerMove
        gs.undoMove()
    
    return bestMove

def look2MoveAhead(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1

    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None

    for playerMove in validMoves:
        gs.makeMove(playerMove, isHuman=False)
        opponentMaxScore = -CHECKMATE

        for i in range(1):
            recrution(gs)

        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()

    return bestPlayerMove

def recrution(gs, count=1):
    opponentsMoves = gs.getValidMoves()
    opponentMaxScore = -CHECKMATE
    turnMultiplier = 1 if gs.whiteToMove else -1

    random.shuffle(opponentsMoves)

    for opponentsMove in opponentsMoves:
        gs.makeMove(opponentsMove, isHuman=False)
        idk = count+1

        if gs.checkmate:
            score = -turnMultiplier * CHECKMATE
        elif gs.stalemate:
            score = STALEMATE
        else:
            score = -turnMultiplier * scoreMaterial(gs.board)

        if score > opponentMaxScore:
            opponentMaxScore = score
        gs.undoMove()
    
    return opponentMaxScore

def minMax():
    pass

def scoreMaterial(board):
    score = 0

    for r in board:
        for square in r:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    
    return score