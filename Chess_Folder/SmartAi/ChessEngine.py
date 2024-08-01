class GameState():
    def __init__(self):
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"]
        ]

        self.moveFunctions = {
            "B": self.getBishopMoves,
            "K": self.getKingMoves,
            "N": self.getKnightMoves,
            "P": self.getPawnMoves,
            "Q": self.getQueenMoves,
            "R": self.getRookMoves
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 5)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]

        self.pieceLocations = {
            "bB": [],
            "bK": [],
            "bN": [],
            "bP": [],
            "bQ": [],
            "bR": [],
            "wB": [],
            "wK": [],
            "wN": [],
            "wP": [],
            "wQ": [],
            "wR": []
        }

        self.importFen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8  ")
        #self.importFen("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10")

        for r in range(7):
            for c in range(7):
                piece = self.board[r][c]

                if piece == "wK":
                    self.whiteKingLocation = (r, c)
                elif piece == "bK":
                    self.blackKingLocation = (r, c)

        self.getPieceLocations()

    def getPieceLocations(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]

                if piece != "--":
                    self.pieceLocations[piece].append((r, c))
    
    def importFen(self, fen):
        row = 0
        col = 0

        boardComplete = False
        castlingRight = [False, False, False, False]

        pieces = [
            "P",
            "B",
            "N",
            "R",
            "Q",
            "K"
        ]

        for i in range(len(fen)):
            if fen[i] != " " and not boardComplete:
                if str.upper(fen[i]) in pieces:
                    piece = str.upper(fen[i])

                    if str.upper(fen[i]) == fen[i]:
                        piece = "w" + piece

                        self.board[row][col] = piece
                        col += 1
                    else:
                        piece = "b" + piece

                        self.board[row][col] = piece
                        col += 1

                elif fen[i].isdigit():
                    piece = "--"

                    for i in range(int(fen[i])):
                        self.board[row][col] = piece
                        col += 1

                elif fen[i] == "/":
                    row += 1
                    col = 0
            else:
                boardComplete = True

            if (str.lower(fen[i]) == "w" or str.lower(fen[i]) == "b") and boardComplete:
                self.whiteToMove = True if str.lower(fen[i]) == "w" else False

                for castling in range(4):
                    if fen[i + 2 + castling] == " ":
                        break
                    else:
                        piece = str.upper(fen[i + 2 + castling])

                        if str.upper(fen[i + 2 + castling]) == fen[i + 2 + castling]:
                            if piece == "Q":
                                castlingRight[2] = True
                            elif piece == "K":
                                castlingRight[0] = True
                        else:
                            if piece == "Q":
                                castlingRight[3] = True
                            elif piece == "K":
                                castlingRight[1] = True
        
        self.currentCastlingRight = CastleRights(castlingRight[0], castlingRight[1], castlingRight[2], castlingRight[3])
        self.castleRightsLog = [CastleRights(
            self.currentCastlingRight.wks, self.currentCastlingRight.bks,
            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs
        )]

    def makeMove(self, move, isHuman=False):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        self.pieceLocations[move.pieceMoved].remove((move.startRow, move.startCol))
        self.pieceLocations[move.pieceMoved].append((move.endRow, move.endCol))

        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                self.pieceLocations[move.pieceCaptured].remove((move.startRow, move.endCol))
            else:
                self.pieceLocations[move.pieceCaptured].remove((move.endRow, move.endCol))

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.pieceLocations[move.pieceMoved[0] + "R"].remove((move.endRow, move.endCol + 1))
                self.pieceLocations[move.pieceMoved[0] + "R"].append((move.endRow, move.endCol - 1))
            else:
                self.pieceLocations[move.pieceMoved[0] + "R"].remove((move.endRow, move.endCol - 2))
                self.pieceLocations[move.pieceMoved[0] + "R"].append((move.endRow, move.endCol + 1))
 
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(
            self.currentCastlingRight.wks, self.currentCastlingRight.bks,
            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs
        ))

        def getPromotionType():
            if move.isPawnPromotion:
                promotion = input("Promote to Q, R, B or N:")

                if str.upper(promotion) == "Q" or str.upper(promotion) == "N" or str.upper(promotion) == "B" or str.upper(promotion) == "R":
                    move.promotionType = str.upper(promotion)

                    self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionType
                else:
                    print("Invalid promotion!")
                    getPromotionType()

        self.enpassantPossibleLog.append(self.enpassantPossible)

        if isHuman:
            getPromotionType()
        else:
            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionType

        if move.isPawnPromotion:
            self.pieceLocations[move.pieceMoved[0] + move.promotionType].append((move.endRow, move.endCol))
            self.pieceLocations[move.pieceMoved].remove((move.endRow, move.endCol))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            self.castleRightsLog.pop()
            newCaslteRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newCaslteRights.wks, newCaslteRights.bks, newCaslteRights.wqs, newCaslteRights.bqs)

            self.checkmate = False
            self.stalemate = False

            self.pieceLocations[move.pieceMoved].append((move.startRow, move.startCol))

            if (move.endRow, move.endCol) in self.pieceLocations[move.pieceMoved]:
                self.pieceLocations[move.pieceMoved].remove((move.endRow, move.endCol))

            if move.isPawnPromotion:
                self.pieceLocations[move.pieceMoved[0] + move.promotionType].remove((move.endRow, move.endCol))
                self.pieceLocations[move.pieceMoved].append((move.endRow, move.endCol))

            if move.pieceCaptured != "--":
                if move.isEnpassantMove:
                    self.pieceLocations[move.pieceCaptured].append((move.startRow, move.endCol))
                else:
                    self.pieceLocations[move.pieceCaptured].append((move.endRow, move.endCol))

            if move.isCastleMove:                    
                if move.endCol - move.startCol == 2:
                    self.pieceLocations[move.pieceMoved[0] + "R"].append((move.endRow, move.endCol + 1))
                    self.pieceLocations[move.pieceMoved[0] + "R"].remove((move.endRow, move.endCol - 1))
                else:
                    self.pieceLocations[move.pieceMoved[0] + "R"].append((move.endRow, move.endCol - 2))
                    self.pieceLocations[move.pieceMoved[0] + "R"].remove((move.endRow, move.endCol + 1))

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
        
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)

                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
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
            for position in self.pieceLocations[piece]:
                r = position[0]
                c = position[1]

                turn = self.board[r][c][0]

                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves
    
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()

            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]

                        if (0 <= j <= 3 and type == "R") or \
                                (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
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
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        
        return inCheck, pins, checks
    
    def squareUnderAttack(self, r, c, allyColor):
        enemyColor = "b" if self.whiteToMove else "w"
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

        for j in range(len(directions)):
            d = directions[j]

            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]

                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]

                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                            (type == "Q") or (i == 1 and type == "K"):

                            return True
                        else:
                            break
                else:
                    break

        knigtMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

        for m in knigtMoves:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    return True  
        
        return False

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])

                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])

                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]

                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"

        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor:
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    
                    inCheck, pins, checks = self.checkForPinsAndChecks()

                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        
        self.getCastleMoves(r, c, moves, allyColor)
    
    def getCastleMoves(self, r, c, moves, allyColor):
        inCheck = self.squareUnderAttack(r, c, allyColor)

        if inCheck:
            return

        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves, allyColor)
            
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves, allyColor)

    def getKingSideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--" and self.board[r][c + 3][0] == allyColor:
            if not self.squareUnderAttack(r, c + 1, allyColor) and not self.squareUnderAttack(r, c + 2, allyColor):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves, allyColor):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--" and self.board[r][c - 4][0] == allyColor:
            if not self.squareUnderAttack(r, c - 1, allyColor) and not self.squareUnderAttack(r, c - 2, allyColor): 
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def getKnightMoves(self, r, c, moves):
        piecePinned = False

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knigtMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"

        for m in knigtMoves:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]

                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[r + moveAmount][c] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))

                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":
                    moves.append(Move((r, c), (  r + 2 * moveAmount, c), self.board))
        
        if c - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False

                    if kingRow == r:
                        if kingCol < c:
                            insideRange = range(kingCol + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1, -1)
                        
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        
                        for i in outsideRange:
                            square = self.board[r][i]

                            if square[0] == enemyColor and (square[1] == "Q" or square[1] == "R"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))

        if c + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False

                    if kingRow == r:
                        if kingCol < c:
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        
                        for i in outsideRange:
                            square = self.board[r][i]

                            if square[0] == enemyColor and (square[1] == "Q" or square[1] == "R"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True

                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isEnpassantMove=True))

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)    

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True 
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]

                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = (self.startRow * 1000) + (self.startCol * 100) + (self.endRow * 10) + self.endCol
        self.promotionType = "Q"
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        self.isCastleMove = isCastleMove

        if self.isEnpassantMove:
            self.pieceCaptured = "bP" if self.pieceMoved == "wP" else "wP"

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