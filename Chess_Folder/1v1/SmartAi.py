import time

pawnPromotions = ["Q", "R", "N", "B"]
dataMoves = {}

DEPTH = 4

def PerftTest(gameState, validMoves):
    file = open("History.txt", "r+")
    file.truncate(0)

    for i in range(DEPTH):
        currentTime = time.time()
        numPosition = MoveGenerationTest(gameState, validMoves, True, None, i + 1)

        print(str.format("Depth: {depth}    Results: {numPositions}     Time: {timeDiff}", depth=i + 1, numPositions=numPosition, timeDiff=round((time.time() - currentTime) * 1000)))

    for text in dataMoves:
        #print(text, dataMoves[text])
        file.write(str.format("{text}: {numPositions}\n", text=text, numPositions=dataMoves[text]))

    file.close()

def MoveGenerationTest(gameState, validMoves, firstMove, moveParent, depth):
    if depth == 0:
        return 1
    
    numPosition = 0

    for move in validMoves:
        if move.isPawnPromotion:
            for char in pawnPromotions:
                move.promotionType = str.upper(char) if gameState.whiteToMove else str.lower(char)

                gameState.makeMove(move)
                nextMoves = gameState.getValidMoves()

                if firstMove:
                    moveParent = move.getChessNotation()
                    dataMoves[moveParent] = 0
                else:
                    dataMoves[moveParent] += 1

                numPosition += MoveGenerationTest(gameState, nextMoves, False, moveParent, depth - 1)

                gameState.undoMove()
        else:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()

            if firstMove:
                moveParent = move.getChessNotation()
                dataMoves[moveParent] = 0
            else:
                dataMoves[moveParent] += 1

            numPosition += MoveGenerationTest(gameState, nextMoves, False, moveParent, depth - 1)

            gameState.undoMove()

    return numPosition