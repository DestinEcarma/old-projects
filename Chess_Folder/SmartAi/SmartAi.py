from cmath import inf
import random
from sqlite3 import Row
from struct import unpack
import time
from tkinter.tix import Tree

file = open("SmartAi/History.txt", "r+")

pieceScore = {
    "K": 0,
    "P": 1,
    "B": 3,
    "N": 3,
    "R": 5,
    "Q": 9,
}

promotionTypes = ["Q", "R", "N", "B"]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 3],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

whitePawnScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

blackPawnScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8]
]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]


rookScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 2, 2, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

piecePositionScores = {"B": bishopScores, "N": knightScores, "wP": whitePawnScores, "bP": blackPawnScores, "Q": queenScores, "R": rookScores}

CHECKMATE = float('inf')
STALEMATE = 0
DEPTH = 4

dataMoves = {}

def findBestMove(gs, validMoves, generatedHash, returnQueue):
    global nextMove, counter, evaluation, captures, castles, promotions, checks, isCheckmate
    nextMove = previousMove = None
    counter = evaluation = castles = promotions = checks = isCheckmate = 0
    previousCaptures = previousCastles = previousPromotions = previousChecks = previousIsCheckmate = 0

    random.shuffle(validMoves)
    #findMoveNegaMax(gs, validMoves, 1 if gs.whiteToMove else -1, DEPTH)
    #findMoveNegaMaxAlphaBeta(gs, validMoves, 1 if gs.whiteToMove else -1, DEPTH, -CHECKMATE, CHECKMATE)

    file.truncate(0)

    hash = generatedHash.zobristHash(gs.board)

    if hash in generatedHash.dataTable.keys():
        print("hash already exist")
        nextMove = generatedHash.dataTable[hash]
    else:
        for i in range(DEPTH):
            counter = evaluation = captures = castles = promotions = checks = isCheckmate = 0
            currentTime = time.time()
            generated = moveGenerationTest(gs, validMoves, i + 1, True, "", -CHECKMATE, CHECKMATE, i + 1,)
            evaluation = generated[1]

            captures -= previousCaptures
            castles -= previousCastles
            promotions -= previousPromotions
            checks -= previousChecks
            isCheckmate -= previousIsCheckmate

            previousCaptures = captures
            previousCastles = castles
            previousPromotions = promotions
            previousChecks = checks
            previousIsCheckmate = isCheckmate

            print(str.format("Depth: {i}    Result: {evaluation}    Captures: {captures}     Time: {currentTime}    Castle: {castles}   Promotions: {promotions}    Checks: {checks}    Checkmates: {checkmates}", i = i + 1, evaluation = evaluation, captures = captures, currentTime = round((time.time() - currentTime) * 1000), castles = castles, promotions = promotions, checks = checks, checkmates = isCheckmate))

            #if nextMove != None and nextMove == previousMove:
                #break
                
            previousMove = nextMove
            
    if nextMove is None:
        nextMove = random.choice(validMoves)

    for text in dataMoves:
        file.write(str.format("{text}: {number}\n", text = text, number = dataMoves[text]))

    generatedHash.dataTable[hash] = nextMove

    returnQueue.put([nextMove, generatedHash.dataTable])

def findMoveMinMax(gs, validMoves, whiteToMove, depth):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove:
        maxScore = -CHECKMATE

        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, False, depth - 1)

            if score > maxScore:
                maxScore = score

                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()

        return maxScore
 
    else:
        minScore = CHECKMATE

        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, True, depth - 1)

            if score < minScore:
                minScore = score

                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()

        return minScore

def moveGenerationTest(gs, validMoves, depth, firstMove, theMove, alpha, beta, givenDepth):
    global nextMove, counter, captures, castles, promotions, checks, isCheckmate
    counter += 1
    numPosition = 0

    turnMultiplier = 1 if gs.whiteToMove else -1

    if depth == 0:
        return [turnMultiplier * scoreBoard(gs), 1]

    maxScore = -CHECKMATE
    
    for move in validMoves:
        if move.isPawnPromotion:
            for i in range(len(promotionTypes)):
                promotions += 1
                move.promotionType = promotionTypes[i]
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()

                if firstMove:
                    theMove = move.getChessNotation()
                    dataMoves[theMove] = 0
                else:
                    dataMoves[theMove] += 1

                if move.pieceCaptured != "--":
                    captures += 1
                if gs.checkmate or gs.stalemate:
                    isCheckmate += 1
                if gs.inCheck:
                    checks += 1
                if move.isCastleMove:
                    castles += 1

                generated = moveGenerationTest(gs, nextMoves, depth - 1, False, theMove, -beta, -alpha, givenDepth)

                score = -generated[0]
                numPosition += generated[1]

                if score > maxScore:
                    maxScore = score

                    if depth == givenDepth:
                        nextMove = move
                
                gs.undoMove()
                
                if maxScore > alpha:
                    alpha = maxScore

                if alpha >= beta:
                    #break
                    pass
        else:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()

            if firstMove:
                theMove = move.getChessNotation()
                dataMoves[theMove] = 0
            else:
                dataMoves[theMove] += 1

            if move.pieceCaptured != "--":
                captures += 1
            if gs.checkmate or gs.stalemate:
                isCheckmate += 1
            if gs.inCheck:
                checks += 1
            if move.isCastleMove:
                castles += 1

            generated = moveGenerationTest(gs, nextMoves, depth - 1, False, theMove, -beta, -alpha, givenDepth)

            score = -generated[0]
            numPosition += generated[1]

            if score > maxScore:
                maxScore = score

                if depth == givenDepth:
                    nextMove = move
            
            gs.undoMove()
            
            if maxScore > alpha:
                alpha = maxScore

            if alpha >= beta:
                #break
                pass
            

    return maxScore, numPosition, theMove

def findMoveNegaMax(gs, validMoves, turnMultiplier, depth):
    global nextMove, counter, evaluation
    counter += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    
    for move in validMoves:
        gs.makeMove(move)
        evaluation += 1
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, -turnMultiplier, depth - 1)

        if score > maxScore:
            maxScore = score

            if depth == DEPTH:
                nextMove = move

        gs.undoMove()
        
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, turnMultiplier, depth, alpha, beta):
    global nextMove, counter, evaluation
    counter += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    
    for move in validMoves:
        if move.isPawnPromotion:
            for i in len(promotionTypes):
                move.promotionType = promotionTypes[i]

                gs.makeMove(move)
                evaluation += 1

                nextMoves = gs.getValidMoves()
                score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, -turnMultiplier, depth - 1, -beta, -alpha)

                if score > maxScore:
                    maxScore = score

                    if depth == DEPTH:
                        nextMove = move

                gs.undoMove()

                if maxScore > alpha:
                    alpha = maxScore

                if alpha >= beta:
                    break
                
        else:
            gs.makeMove(move)
            evaluation += 1

            nextMoves = gs.getValidMoves()
            score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, -turnMultiplier, depth - 1, -beta, -alpha)

            if score > maxScore:
                maxScore = score

                if depth == DEPTH:
                    nextMove = move

            gs.undoMove()

            if maxScore > alpha:
                alpha = maxScore

            if alpha >= beta:
                break

    return maxScore
             
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0

    for r in range(len(gs.board)):
        for c in range(len(gs.board[r])):
            square = gs.board[r][c]
            piecePositionScore = 0

            if square == "--": continue

            if square[1] in piecePositionScores:
                if square[1] == "P":
                    piecePositionScore = piecePositionScores[square][r][c]
                else:
                    piecePositionScore = piecePositionScores[square[1]][r][c]

            if square[0] == "w":
                score += pieceScore[square[1]] + (piecePositionScore * 0.1)
            elif square[0] == "b":
                score -= pieceScore[square[1]] + (piecePositionScore * 0.1)
    
    return score

def scoreMaterial(board):
    score = 0

    for r in range(len(board)):
        for square in r:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    
    return score