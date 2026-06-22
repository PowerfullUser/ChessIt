from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import chess
import chess.pgn
import stockfish
import sys
import os

name = "ChessIt"
version = "1"
display_name = f"{name} {version}"

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        board_widget = QWidget()
        board_widget.setFixedWidth(560)
        board_widget.setFixedHeight(560)

        self.board = chess.Board()

        self.engine = stockfish.Stockfish(path=os.path.abspath("stockfish/stockfish.exe"))
        self.engine.set_depth(10)
        
        self.selected_square = None

        self.chess_board = QGridLayout()
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        board_widget.setLayout(self.chess_board)

        outer_widget = QWidget()
        outer_layout = QHBoxLayout()

        board_layout = QVBoxLayout()

        self.eval_bar = QLabel()
        self.eval_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eval_bar.setText("Evaluation will be provided here")
        self.eval_bar.setFixedHeight(30)
        self.eval_bar.setStyleSheet("border: 2px solid #000; background-color: #fff;")
        board_layout.addWidget(self.eval_bar)

        board_layout.addWidget(board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        outer_layout.addLayout(board_layout)

        side_panel = QWidget()
        side_panel.setFixedWidth(600)
        side_panel.setStyleSheet("border: 2px solid #000; background-color: #fff;")

        layout = QVBoxLayout()

        inner_layout = QHBoxLayout()

        self.best_move_label = QLabel()
        self.best_move_label.setFont(QFont("Segoe UI", 12))
        self.best_move_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_move_label.setText("Best Move:")
        self.best_move_label.setStyleSheet("border: none;")
        inner_layout.addWidget(self.best_move_label)

        self.accuracy_label = QLabel()
        self.accuracy_label.setFont(QFont("Segoe UI", 12))
        self.accuracy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accuracy_label.setText("Accuracy: ")
        self.accuracy_label.setStyleSheet("border: none;")
        inner_layout.addWidget(self.accuracy_label)

        layout.addLayout(inner_layout)

        self.text_editor = QTextEdit()
        self.text_editor.setDisabled(True)
        self.text_editor.setFont(QFont("Segoe UI", 14))
        layout.addWidget(self.text_editor)

        toolbar = QToolBar()
        toolbar.setStyleSheet("border: none;")

        reset_board = QPushButton("Reset Board", self)
        reset_board.setStyleSheet("border: 2px solid #000; padding-top: 5px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px; border-radius: 5px; margin-right: 5px;")
        reset_board.setStyle(QStyleFactory.create("fusion"))
        reset_board.clicked.connect(self.reset_board)
        toolbar.addWidget(reset_board)

        import_pgn = QPushButton("Import PGN", self)
        import_pgn.setStyleSheet("border: 2px solid #000; padding-top: 5px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px; border-radius: 5px; margin-right: 5px;")
        import_pgn.setStyle(QStyleFactory.create("fusion"))
        import_pgn.clicked.connect(self.import_pgn)
        toolbar.addWidget(import_pgn)

        save_pgn = QPushButton("Save PGN", self)
        save_pgn.setStyleSheet("border: 2px solid #000; padding-top: 5px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px; border-radius: 5px; margin-right: 5px;")
        save_pgn.setStyle(QStyleFactory.create("fusion"))
        save_pgn.clicked.connect(self.save_pgn)
        toolbar.addWidget(save_pgn)

        layout.addWidget(toolbar)

        side_panel.setLayout(layout)

        outer_layout.addWidget(side_panel)

        outer_widget.setLayout(outer_layout)

        self.setCentralWidget(outer_widget)
        
        self.load_piece_images()
        self.create_board()

    def load_piece_images(self):
        self.piece_images = {
            "P" : QPixmap("Piece Images/wp.png"),
            "B" : QPixmap("Piece Images/wb.png"),
            "N" : QPixmap("Piece Images/wn.png"),
            "R" : QPixmap("Piece Images/wr.png"),
            "Q" : QPixmap("Piece Images/wq.png"),
            "K" : QPixmap("Piece Images/wk.png"),
            "p" : QPixmap("Piece Images/bp.png"),
            "b" : QPixmap("Piece Images/bb.png"),
            "n" : QPixmap("Piece Images/bn.png"),
            "r" : QPixmap("Piece Images/br.png"),
            "q" : QPixmap("Piece Images/bq.png"),
            "k" : QPixmap("Piece Images/bk.png")
        }

    def create_board(self):
        self.chess_board.setSpacing(0)
        self.chess_board.setContentsMargins(0,0,0,0)

        for i in range(8):
            self.chess_board.setColumnStretch(i, 1)
            self.chess_board.setRowStretch(i, 1)

        for row in range(8):
            for col in range(8):
                label = QLabel()
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                label.setScaledContents(True)
                label.mousePressEvent = lambda event, r=row, c=col: self.square_clicked(r, c)

                if (row+col) % 2 == 0:
                    label.setStyleSheet("background-color: #aaa;")
                elif (row+col) % 2 == 1:
                    label.setStyleSheet("background-color: #fff;")

                self.chess_board.addWidget(label, row, col)
                self.squares[row][col] = label

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)

            file = chess.square_file(square)
            rank = chess.square_rank(square)

            row = 7 - rank
            col = file

            label = self.squares[row][col]

            if piece:
                pix = self.piece_images[piece.symbol()]
                size = min(70, 70)
                label.setPixmap(
                    pix.scaled(
                        size,
                        size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )
            else:
                label.clear()

    def square_clicked(self, row, col):
        square = chess.square(col, 7-row)

        if self.selected_square is None:
            self.selected_square = square
            self.highlight_square(square)
            return
        
        if self.selected_square is square:
            self.selected_square = None
            self.unhighlight_square()
            return
            
        move = chess.Move(self.selected_square, square)
            
        if move in self.board.legal_moves:
            self.board.push(move)
            self.create_board()
            self.engine.set_fen_position(self.board.fen())

            self.evaluation()
            self.accuracy()
            self.put_pgn()
        else:
                print("Illegal Move")

        self.selected_square = None

    def put_pgn(self):
        pgn = chess.pgn.Game.from_board(self.board)
        self.text_editor.setText(str(pgn))

    def highlight_square(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        row = 7-rank
        col = file

        label = self.squares[row][col]
        label.setStyleSheet("background-color: #ebb734")

    def unhighlight_square(self):
        for row in range(8):
            for col in range(8):
                label = self.squares[row][col]
                
                if (row+col) % 2 == 0:
                    label.setStyleSheet("background-color: #aaa;")
                elif (row+col) % 2 == 1:
                    label.setStyleSheet("background-color: #fff;")

    def evaluation(self):
        self.engine.set_fen_position(self.board.fen())

        best = self.engine.get_best_move()

        if not best == None:
            best_move = chess.Move.from_uci(best)
            self.best_move_label.setText(f"Best Move: <b>{self.board.san(best_move)}</b>")
        else:
            self.best_move_label.setText(f"End of Game")

        eval = self.engine.get_evaluation()
        value = eval["value"]

        if eval["type"] == "mate":
            text = f"Mate in {abs(value)}"
        else:
            text = f"{value/100}"
        
        self.eval_bar.setText(text)

    def reset_board(self):
        self.board.reset()
        self.create_board()
        self.selected_square = None
        self.eval_bar.setText("Evaluation will be provided here")
        self.best_move_label.setText("Best Move: ")
        self.accuracy_label.setText("Accuracy: ")
        self.text_editor.clear()

    def import_pgn(self):
        file_dialog, _ = QFileDialog.getOpenFileName(self, "Open PGN", "", "PGN Files (*.pgn);")

        if _ and file_dialog:
            if not file_dialog.endswith(".pgn"):
                pass
            else:
                try:
                    self.board.reset()
                    with open(file_dialog, "r") as pgn:
                        game = chess.pgn.read_game(pgn)

                        for moves in game.mainline_moves():
                            self.board.push(moves)

                        self.create_board()
                        self.evaluation()
                        self.accuracy()
                        self.selected_square = None

                    with open(file_dialog, "r") as f:
                        text = f.read()
                        self.text_editor.setPlainText(text)
                except:
                    pass
    
    def accuracy(self):
        cp_losses = []
        moves = list(self.board.move_stack)
        temp = chess.Board()

        for move in moves:
            self.engine.set_fen_position(temp.fen())
            best = self.engine.get_best_move()

            if best is None:
                break

            best_move = chess.Move.from_uci(best)

            temp.push(best_move)
            self.engine.set_fen_position(temp.fen())
            best_eval = self.engine.get_evaluation()["value"]
            temp.pop()

            temp.push(move)
            self.engine.set_fen_position(temp.fen())
            played_eval = self.engine.get_evaluation()["value"]
            temp.pop()

            cp_losses.append(abs(best_eval - played_eval))
            temp.push(move)

            if not cp_losses:
                self.accuracy_label.setText("100.0")
                return
            
            avg_loss = sum(cp_losses) / len(cp_losses)
            accuracy = max(0, 100 - avg_loss /2)
            self.accuracy_label.setText(f"Accuracy: <b>{str(round(accuracy, 2))}</b>")

    def save_pgn(self):
        file_dialog, _ = QFileDialog.getSaveFileName(self, "Save File", "", "PGN Files (*.pgn);; Text Files (*.txt);; All Files (*.*)")

        if _ and file_dialog:
            with open(file_dialog, "w") as f:
                text = self.text_editor.toPlainText()
                f.write(text)
                f.close()
        else:
            pass

app = QApplication(sys.argv)
app.setApplicationName(name)
app.setApplicationVersion(version)
app.setApplicationDisplayName(display_name)
window = MainWindow()
window.setWindowIcon(QIcon("Piece Images/ChessIt.png"))
window.showMaximized()
app.exec()