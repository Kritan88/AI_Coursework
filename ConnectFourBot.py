# connect_four_bot.py

class ConnectFourBot:
    def __init__(self, board):
        self.board = board
        self.current_player = "O"

    def choose_move(self, board, rows, columns):
        """Calculate the best move for the bot using a simple heuristic.
        
        Returns:
            int: The column index (1-based) for the best move.
        """
        pass

    def is_valid_move(self, col):
        """Check if a column is a valid move."""
        col -= 1  # Convert to 0-based index
        return 0 <= col < len(self.board[0]) and self.board[0][col] == " "

    def make_move(self, board, col, player, rows):
        """Simulate dropping a disc in a column."""
        col -= 1  # Convert to 0-based index
        for row in range(rows - 1, -1, -1):
            if board[row][col] == " ":
                board[row][col] = player
                break

    def undo_move(self, board, col, rows):
        """Undo the last move in the given column."""
        col -= 1  # Convert to 0-based index
        for row in range(rows):
            if board[row][col] != " ":
                board[row][col] = " "
                break

    def is_winning_move(self, board, player, rows, columns):
        """Check if the given player has a winning move."""
        for row in range(rows):
            for col in range(columns):
                if (
                    self.check_direction(board, row, col, 1, 0, player) or  # Horizontal
                    self.check_direction(board, row, col, 0, 1, player) or  # Vertical
                    self.check_direction(board, row, col, 1, 1, player) or  # Diagonal /
                    self.check_direction(board, row, col, 1, -1, player)    # Diagonal \
                ):
                    return True
        return False

    def check_direction(self, board, row, col, delta_row, delta_col, player):
        """Check a specific direction for a win condition."""
        for i in range(4):
            r, c = row + i * delta_row, col + i * delta_col
            if (
                r < 0 or r >= len(board) or
                c < 0 or c >= len(board[0]) or
                board[r][c] != player
            ):
                return False
        return True

    def compute_heuristic_value():
        """Compute an estimate of the cost to a win."""
        pass
