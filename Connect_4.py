import numpy as np

class Connect4:
    """Main game class for Connect 4"""
    def __init__(self, rows=6, cols=7):
        """
        Initialize Connect 4 game board and state
        
        Args:
            rows: Number of rows in game board (default: 6)
            cols: Number of columns in game board (default: 7)
        """
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        self.reset()

    def reset(self):
        """
        Reset the game to initial state
        
        Resets:
        - Board to all zeros
        - Game over flag to False
        - Winner to None
        - Current player to 1 (Player 1 starts)
        - Move history to empty list
        """
        self.board.fill(0)
        self.game_over = False
        self.winner = None
        self.current_player = 1
        self.moves_history = []

    def drop_piece(self, col):
        """
        Attempt to place current player's piece in specified column
        
        Args:
            col: Column index (0-based) where piece should be dropped
            
        Returns:
            bool: True if move was successful, False if invalid
            
        Side Effects:
        - Updates board state
        - Updates game over status if win/draw detected
        - Switches current player if move successful
        - Appends move to history
        """
        if self.game_over or col < 0 or col >= self.cols:
            return False

        for row in range(self.rows-1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.current_player
                self.moves_history.append((self.current_player, col))

                if self.check_win(row, col):
                    self.game_over = True
                    self.winner = self.current_player
                elif np.all(self.board != 0):
                    self.game_over = True

                self.current_player = 3 - self.current_player
                return True
        return False

    def check_win(self, row, col):
        """
        Check if last move resulted in a win
        
        Args:
            row: Row index (0-based) of last move
            col: Column index (0-based) of last move
            
        Returns:
            bool: True if move created 4-in-a-row, False otherwise
            
        Note:
            Checks all 4 possible directions (horizontal, vertical, both diagonals)
        """
        player = self.board[row][col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1
            for step in [1, -1]:
                r, c = row + dr * step, col + dc * step
                while (0 <= r < self.rows and 0 <= c < self.cols 
                       and self.board[r][c] == player):
                    count += 1
                    r += dr * step
                    c += dc * step
                    if count >= 4:
                        return True
        return False

    def get_valid_moves(self):
        """
        Get list of currently playable columns
        
        Returns:
            list: List of column indices (0-based) with at least one empty space
            
        Note:
            A column is valid if top row (index 0) is empty
        """
        return [col for col in range(self.cols) if self.board[0][col] == 0]

    def display(self):
        """
        Print current game state to console
        
        Shows:
        - Column numbers header
        - Board state with player pieces (X/O) or empty spaces (.)
        - Current player turn
        - Game result if game over
        - Move history
        
        Example Output:
          0 1 2 3 4 5 6
        | . . . . . . . |
        | . . . . . . . |
        | . . X . . . . |
        | . . O . . . . |
        | . . X . . . . |
        | . O O X . . . |
        ----------------
        Current player: Player 1 (X)
        """
        print("\n  " + " ".join(str(i) for i in range(self.cols)))
        for row in self.board:
            print("| " + " ".join(
                "X" if cell == 1 else "O" if cell == 2 else "." for cell in row
            ) + " |")
        print("-" * (2 * self.cols + 3))
        print(f"Current player: {'Player 1 (X)' if self.current_player == 1 else 'Player 2 (O)'}")

        if self.game_over:
            if self.winner:
                print(f"\nPlayer {self.winner} ({'X' if self.winner == 1 else 'O'}) wins!")
            else:
                print("\nIt's a draw!")

        print(f"Move history: {self.moves_history}")