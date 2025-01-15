class ConnectFour:
    def __init__(self):
        """Initialize the Connect Four game board."""
        self.rows = 6
        self.columns = 7
        self.board = [[" " for _ in range(self.columns)] for _ in range(self.rows)]
        self.player_X = "X"  # Player 1 starts with 'X'
        self.player_O = "O"
        self.current_player = self.player_X
        self.iteration = 0

    def display_board(self):
        """Print the current state of the board."""
        for row in self.board:
            print("|" + "|".join(row) + "|")
        print(" " + " ".join(map(str, range(1, self.columns + 1))))

    def drop_disc(self, column):
        """Drop a disc into the specified column."""
        column -= 1  # Convert to 0-based index
        if column < 0 or column >= self.columns or self.board[0][column] != " ":
            print("Invalid move. Try again.")
            return False

        for row in reversed(self.board):
            if row[column] == " ":
                if self.current_player == self.player_X:
                    row[column] = self.player_X
                    return True
                else:
                    row[column] = self.player_O
                    return True


    def check_winner(self):
        """Check if the current player has won the game.

        Returns:
            bool: True if the current player wins, False otherwise.
        """
        # Check horizontal, vertical, and diagonal directions
        for row in range(self.rows):
            for col in range(self.columns):
                if (
                    self.check_direction(row, col, 1, 0) or  # Horizontal
                    self.check_direction(row, col, 0, 1) or  # Vertical
                    self.check_direction(row, col, 1, 1) or  # Diagonal /
                    self.check_direction(row, col, 1, -1)    # Diagonal \
                ):
                    return True
        return False

    def check_direction(self, row, col, delta_row, delta_col):
        """Check a specific direction for a win condition.

        Args:
            row (int): Starting row index.
            col (int): Starting column index.
            delta_row (int): Row increment.
            delta_col (int): Column increment.

        Returns:
            bool: True if there are 4 in a row in the given direction, False otherwise.
        """
        disc = self.board[row][col]
        if disc == " ":
            return False

        for i in range(1, 4):
            r, c = row + i * delta_row, col + i * delta_col
            if r < 0 or r >= self.rows or c < 0 or c >= self.columns or self.board[r][c] != disc:
                return False

        return True
    
    def switch_player(self):
        """Switch to the other player."""
        self.current_player = self.player_O if self.current_player == self.player_X else self.player_X

    def play(self):
        """Start the game loop."""
        print("Welcome to Connect Four!")
        while True:
            self.display_board()
            if self.current_player == self.player_X:
                # player_X's turn
                try:
                    column = int(input(f"Player {self.player_X}, choose a column (1-{self.columns}): "))
                    if self.drop_disc(column):
                        if self.check_winner():
                            self.display_board()
                            print(f"Player {self.player_X} wins!")
                            break
                        self.switch_player()
                except ValueError:
                    print("Invalid input. Please try again.")
            else:
                # player_O's turn
                try:
                    column = int(input(f"Player {self.player_O}, choose a column (1-{self.columns}): "))
                    # column = ConnectFourBot.choose_move(self.board)
                    if self.drop_disc(column):
                        if self.check_winner():
                            self.display_board()
                            print(f"Player {self.player_O} wins!")
                            break
                        self.switch_player()
                except ValueError:
                    print("Invalid input. Please try again.")
            self.iteration += .5
            


# Run the game
if __name__ == "__main__":
    game = ConnectFour()
    game.play()
