FEN = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - "

RANKSTOROWS = [7, 6, 5, 4, 3, 2, 1, 0]
FILESTOCOLS = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7
}

class GameState:
    def __init__(self):
        self.whiteToMove = True

        self.checkmate = False
        self.stalemate = False
        self.inCheck = False

        self.board = [[]]
        self.moveLog = []
        self.checks = []
        self.pins = []
    
        self.enpassantPossible = ()
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        
        self.moveFunctions = {
            "B": self.getBishopMoves,
            "K": self.getKingMoves,
            "N": self.getKnightMoves,
            "P": self.getPawnMoves,
            "Q": self.getQueenMoves,
            "R": self.getRookMoves
        }

        self.pieceLocations = {
            "B": [],
            "K": [],
            "N": [],
            "P": [],
            "Q": [],
            "R": [],
            "b": [],
            "k": [],
            "n": [],
            "p": [],
            "q": [],
            "r": []
        }

        self.importFen(FEN)

        self.getAllPossibleMoves()

    def importFen(self, fenString):
        fenString = fenString.split(" ")

        fenBoard = fenString[0]
        fenTurn = fenString[1]
        fenCastling = fenString[2]
        fenEnpassant = fenString[3]

        row = 0

        castlingRight = {
            "K": False,
            "Q": False,
            "k": False,
            "q": False
	    }

        for char in fenBoard:
            if char == "/":
                self.board.append([])
                row += 1
            else:
                if char.isnumeric():
                    for i in range(int(char)):
                        self.board[row].append("-")
                else:
                    self.board[row].append(char)

        self.getPieceLocations()
        self.getKingLocations()
            
        if fenTurn[0] == "b":
            self.whiteToMove = False

        if fenCastling[0] != "-":
            for char in fenCastling:
                castlingRight[char] = True

        self.currentCastlingRight = CastleRights(castlingRight["K"], castlingRight["Q"], castlingRight["k"], castlingRight["q"])
        self.castleRightsLog = [CastleRights(
            self.currentCastlingRight.K, self.currentCastlingRight.Q,
            self.currentCastlingRight.k, self.currentCastlingRight.q
        )]

        if fenEnpassant != "-":
            self.enpassantPossible = (RANKSTOROWS[int(fenEnpassant[1]) - 1], FILESTOCOLS[fenEnpassant[0]])
        self.enpassantPossibleLog = [self.enpassantPossible]
        
    def getPieceLocations(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]

                if piece != "-":
                    self.pieceLocations[piece].append((row, col))

    def getKingLocations(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                piece = self.board[row][col]

                if piece == "K":
                    self.whiteKingLocation = (row, col)
                elif piece == "k":
                    self.blackKingLocation = (row, col)

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "-"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.whiteToMove = not self.whiteToMove

        self.pieceLocations[move.pieceMoved].remove((move.startRow, move.startCol))
        self.pieceLocations[move.pieceMoved].append((move.endRow, move.endCol))

        if move.pieceCaptured != "-" and not move.isEnpassantMove:
            self.pieceLocations[move.pieceCaptured].remove((move.endRow, move.endCol))

        if move.pieceMoved == "K":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "k":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                rookCol = move.endCol + 1
                rookNewCol = move.endCol - 1
                rook = self.board[move.endRow][rookCol]

                self.pieceLocations[rook].remove((move.endRow, rookCol))
                self.pieceLocations[rook].append((move.endRow, rookNewCol))

                self.board[move.endRow][rookNewCol] = rook
                self.board[move.endRow][rookCol] = "-"
            else:
                rookCol = move.endCol - 2
                rookNewCol = move.endCol + 1
                rook = self.board[move.endRow][rookCol]

                self.pieceLocations[rook].remove((move.endRow, rookCol))
                self.pieceLocations[rook].append((move.endRow, rookNewCol))

                self.board[move.endRow][rookNewCol] = rook
                self.board[move.endRow][rookCol] = "-"

        if move.isPawnPromotion:
            move.promotionType = str.lower(move.promotionType) if self.whiteToMove else str.upper(move.promotionType)
            self.board[move.endRow][move.endCol] = move.promotionType

            self.pieceLocations[move.pieceMoved].remove((move.endRow, move.endCol))
            self.pieceLocations[move.promotionType].append((move.endRow, move.endCol))

        if move.isEnpassantMove:
            enemyPawn = self.board[move.startRow][move.endCol]
            self.pieceLocations[enemyPawn].remove((move.startRow, move.endCol))

            self.board[move.startRow][move.endCol] = "-"

        if str.upper(move.pieceMoved) == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(
            self.currentCastlingRight.K, self.currentCastlingRight.Q,
            self.currentCastlingRight.k, self.currentCastlingRight.q
        ))
        self.enpassantPossibleLog.append(self.enpassantPossible)
        self.moveLog.append(move)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            self.checkmate = False
            self.stalemate = False

            self.pieceLocations[move.pieceMoved].append((move.startRow, move.startCol))

            if move.pieceCaptured != "-" and not move.isEnpassantMove:
                self.pieceLocations[move.pieceCaptured].append((move.endRow, move.endCol))

            if move.pieceMoved == "K":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "k":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    rookNewCol = move.endCol + 1
                    rookCol = move.endCol - 1
                    rook = self.board[move.endRow][rookCol]

                    self.pieceLocations[rook].append((move.endRow, rookNewCol))
                    self.pieceLocations[rook].remove((move.endRow, rookCol))

                    self.board[move.endRow][rookNewCol] = rook
                    self.board[move.endRow][rookCol] = "-"
                else:
                    rookNewCol = move.endCol - 2
                    rookCol = move.endCol + 1
                    rook = self.board[move.endRow][rookCol]

                    self.pieceLocations[rook].append((move.endRow, rookNewCol))
                    self.pieceLocations[rook].remove((move.endRow, rookCol))

                    self.board[move.endRow][rookNewCol] = rook
                    self.board[move.endRow][rookCol] = "-"

            if move.isPawnPromotion:
                type = str.upper(move.promotionType) if self.whiteToMove else str.lower(move.promotionType)
                self.pieceLocations[type].remove((move.endRow, move.endCol))
            else:
                self.pieceLocations[move.pieceMoved].remove((move.endRow, move.endCol))

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "-"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

                self.pieceLocations[move.pieceCaptured].append((move.startRow, move.endCol))

            self.castleRightsLog.pop()
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            self.currentCastlingRight = CastleRights(
                self.castleRightsLog[-1].K, self.castleRightsLog[-1].Q,
                self.castleRightsLog[-1].k, self.castleRightsLog[-1].q
            )

    def updateCastleRights(self, move):
        if move.pieceMoved == "K":
            self.currentCastlingRight.K = False
            self.currentCastlingRight.Q = False
        elif move.pieceMoved == "k":
            self.currentCastlingRight.k = False
            self.currentCastlingRight.q = False
        elif move.pieceMoved == "R":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.Q = False
                elif move.startCol == 7:
                    self.currentCastlingRight.K = False
        elif move.pieceMoved == "r":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.q = False
                elif move.startCol == 7:
                    self.currentCastlingRight.k = False

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]

                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                
                validSquares = []

                if str.upper(pieceChecking) == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)

                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if str.upper(moves[i].pieceMoved) != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    def getAllPossibleMoves(self):
        moves = []

        for piece in self.pieceLocations:
            if self.whiteToMove and str.upper(piece) == piece:
                for square in self.pieceLocations[piece]:
                    self.moveFunctions[str.upper(piece)](square[0], square[1], moves)
            elif not self.whiteToMove and str.lower(piece) == piece:
                for square in self.pieceLocations[piece]:
                    self.moveFunctions[str.upper(piece)](square[0], square[1], moves)

        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            startRow, startCol = self.whiteKingLocation
        else:
            startRow, startCol = self.blackKingLocation

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()

            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece != "-":
                        ally = (self.whiteToMove and str.upper(endPiece) == endPiece) or (not self.whiteToMove and str.lower(endPiece) == endPiece)
                        enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                        if ally and str.upper(endPiece) != "K":
                            if possiblePin == ():
                                possiblePin = (endRow, endCol, d[0], d[1])
                            else:
                                break
                        elif enemy:
                            type = str.upper(endPiece)

                            if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                    (i == 1 and type == "P" and ((endPiece == "P" and 6 <= j <= 7) or (endPiece == "p" and 4 <= j <= 5))) or \
                                        (type == "Q") or (i == 1 and type == "K"):

                                if possiblePin == ():
                                    inCheck = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                                    break
                                else:
                                    pins.append(possiblePin)
                                    break
                            else:
                                break
                else:
                    break

        knigtMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in knigtMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                enemy = (self.whiteToMove and endPiece == "n") or (not self.whiteToMove and endPiece == "N")

                if enemy:
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return inCheck, pins, checks

    def squareUnderAttack(self, row, col):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]

            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece != "-":
                        ally = (self.whiteToMove and str.upper(endPiece) == endPiece) or (not self.whiteToMove and str.lower(endPiece) == endPiece)
                        enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                        if ally:
                            break
                        elif enemy:
                            type = str.upper(endPiece)

                            if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                    (i == 1 and type == "P" and ((endPiece == "P" and 6 <= j <= 7) or (endPiece == "p" and 4 <= j <= 5))) or \
                                        (type == "Q") or (i == 1 and type == "K"):

                                return True
                            else:
                                break
                else:
                    break
        
        knigtMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in knigtMoves:
            endRow = row + m[0]
            endCol = col + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    enemy = (self.whiteToMove and endPiece == "n") or (not self.whiteToMove and endPiece == "N")

                    if enemy:
                        return True
        
        return False

    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])

                if str.upper(self.board[row][col]) != "Q":
                    self.pins.remove(self.pins[i])

                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                        if endPiece == "-":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif enemy:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)

        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                if enemy:
                    if self.whiteToMove:
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)

                    inCheck, pins, checks = self.checkForPinsAndChecks()

                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))

                    if self.whiteToMove:
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

        self.getCastleMoves(row, col, moves)

    def getCastleMoves(self, row, col, moves):
        inCheck = self.squareUnderAttack(row, col)
        rookAlly = "R" if self.whiteToMove else "r"

        if inCheck:
            return

        if (self.whiteToMove and self.currentCastlingRight.K) or (not self.whiteToMove and self.currentCastlingRight.k):
            self.getKingSideCastleMoves(row, col, moves, rookAlly)

        if (self.whiteToMove and self.currentCastlingRight.Q) or (not self.whiteToMove and self.currentCastlingRight.q):
            self.getQueenSideCastleMoves(row, col, moves, rookAlly)

    def getKingSideCastleMoves(self, row, col, moves, ally):
        if self.board[row][col + 1] == "-" and self.board[row][col + 2] == "-" and self.board[row][col + 3] == ally:
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, row, col, moves, ally):
        if self.board[row][col - 1] == "-" and self.board[row][col - 2] == "-" and self.board[row][col - 3] == "-" and self.board[row][col - 4] == ally:
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))

    def getKnightMoves(self, row, col, moves):
        piecePinned = False

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knigtMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in knigtMoves:
            endRow = row + m[0]
            endCol = col + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                    if enemy:
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            kingRow, kingCol = self.blackKingLocation

        if self.board[row + moveAmount][col] == "-":
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, col), (row + moveAmount, col), self.board))

                if row == startRow and self.board[row + 2 * moveAmount][col] == "-":
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))

        if col - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                endPiece = self.board[row + moveAmount][col - 1]

                if endPiece != "-":
                    enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                    if enemy:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board))
                
                if (row + moveAmount, col - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False

                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        
                        for i in insideRange:
                            if self.board[row][i] != "-":
                                blockingPiece = True
                        
                        for i in outsideRange:
                            square = self.board[row][i]
                            enemy = (self.whiteToMove and (square == "q" or square == "r")) or (not self.whiteToMove and (square == "Q" or square == "R"))

                            if enemy:
                                attackingPiece = True
                            elif square != "-":
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isEnpassantMove=True))

        if col + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                endPiece = self.board[row + moveAmount][col + 1]

                if endPiece != "-":
                    enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                    if enemy:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board))

                if (row + moveAmount, col + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False

                    if kingRow == row:
                        if kingCol < col:
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        
                        for i in insideRange:
                            if self.board[row][i] != "-":
                                blockingPiece = True
                        
                        for i in outsideRange:
                            square = self.board[row][i]
                            enemy = (self.whiteToMove and (square == "q" or square == "r")) or (not self.whiteToMove and (square == "Q" or square == "R"))

                            if enemy:
                                attackingPiece = True
                            elif square != "-":
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isEnpassantMove=True))

    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True 
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        enemy = (self.whiteToMove and str.lower(endPiece) == endPiece) or (not self.whiteToMove and str.upper(endPiece) == endPiece)

                        if endPiece == "-":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif enemy:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

class CastleRights:
    def __init__(self, K, Q, k, q):
        self.K = K
        self.Q = Q
        self.k = k
        self.q = q

class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start, target, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = target[0]
        self.endCol = target[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isEnpassantMove = isEnpassantMove
        self.isCastleMove = isCastleMove

        self.isPawnPromotion = (self.pieceMoved == "P" and self.endRow == 0) or (self.pieceMoved == "p" and self.endRow == 7)
        self.promotionType = "Q"

        self.moveID = (self.startRow * 1000) + (self.startCol * 100) + (self.endRow * 10) + self.endCol

        if self.isEnpassantMove:
            self.pieceCaptured = "p" if str.upper(self.pieceMoved) == self.pieceMoved else "P"
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        if self.isPawnPromotion:
            return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol) + str.lower(self.promotionType)
        else:
            return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
