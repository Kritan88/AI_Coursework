import math

class AdversarialBot:
    """AI player using minimax algorithm with alpha-beta pruning"""
    def __init__(self, 
                 board, 
                 current_player, 
                 valid_moves, 
                 move_number, 
                 player_type, 
                 depth=5):
        """
        Initialize adversarial search bot
        
        Args:
            board: 2D list representing current game state
            current_player: Integer ID of current player (1 or 2)
            valid_moves: List of playable column indices
            move_number: Current move count in the game
            player_type: Player identification metadata
            depth: Search depth for minimax algorithm (default: 5)
        """
        self.board = board
        self.current_player = current_player
        self.valid_moves = valid_moves
        self.move_number = move_number
        self.player_type = player_type
        self.depth = depth
        
        self.opponent = 3 - self.current_player
        self.rows = len(board)
        self.cols = len(board[0]) if self.rows > 0 else 0

    def make_best_move(self):
        """
        Determine optimal move using minimax with alpha-beta pruning
        
        Returns:
            int: Column index of best move, or None if no valid moves
        """
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        for col in self.valid_moves:
            row = self.get_next_open_row(col)
            if row is None:
                continue
                
            # Create new board state
            new_board = [r[:] for r in self.board]
            new_board[row][col] = self.current_player
            
            # Evaluate the move
            score = self.minimax(
                board=new_board,
                depth=self.depth - 1,
                alpha=alpha,
                beta=beta,
                is_maximizing=False,
                current_player=self.opponent
            )
            
            # Update best move if this is better
            if score > best_score:
                best_score = score
                best_move = col
                
            # Update alpha and check for pruning
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
                
        return best_move

    def minimax(self, 
                board, 
                depth, 
                alpha, 
                beta, 
                is_maximizing, 
                current_player):
        """
        Recursive minimax implementation with alpha-beta pruning
        
        Args:
            board: 2D list representing current game state
            depth: Current search depth remaining
            alpha: Alpha value for alpha-beta pruning
            beta: Beta value for alpha-beta pruning
            is_maximizing: Boolean indicating if current player is maximizer
            current_player: ID of player to move in current state
            
        Returns:
            float: Heuristic score of board position
        """
        # Check terminal states
        winner = self.get_winner(board)
        if winner == self.current_player:
            return 10000 + depth  # Prefer wins in fewer moves
        elif winner == self.opponent:
            return -10000 - depth  # Prefer losses in more moves
        elif self.is_board_full(board) or depth == 0:
            return self.evaluate_board(board, current_player)

        # Maximizing player's turn
        if is_maximizing:
            max_score = -math.inf
            for col in self.get_valid_moves_from_board(board):
                row = self.get_next_open_row_from_board(board, col)
                if row is None:
                    continue
                    
                new_board = [r[:] for r in board]
                new_board[row][col] = current_player
                
                score = self.minimax(
                    board=new_board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_maximizing=False,
                    current_player=3 - current_player
                )
                
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break
                    
            return max_score
            
        # Minimizing player's turn
        else:
            min_score = math.inf
            for col in self.get_valid_moves_from_board(board):
                row = self.get_next_open_row_from_board(board, col)
                if row is None:
                    continue
                    
                new_board = [r[:] for r in board]
                new_board[row][col] = current_player
                
                score = self.minimax(
                    board=new_board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_maximizing=True,
                    current_player=3 - current_player
                )
                
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if beta <= alpha:
                    break
                    
            return min_score

    def evaluate_board(self, board, player):
        """
        Static evaluation function for board state
        
        Args:
            board: 2D list representing game state
            player: ID of player to evaluate position for
            
        Returns:
            int: Numerical score representing position advantage
        """
        score = 0
        
        # Center column preference
        center_col = self.cols // 2
        for r in range(self.rows):
            if board[r][center_col] == player:
                score += 3
        
        # Evaluate horizontal, vertical, and diagonal potentials
        score += self.evaluate_lines(board, player, 1, 0)  # Horizontal
        score += self.evaluate_lines(board, player, 0, 1)  # Vertical
        score += self.evaluate_lines(board, player, 1, 1)  # Diagonal /
        score += self.evaluate_lines(board, player, 1, -1)  # Diagonal \
        
        return score

    def evaluate_lines(self, board, player, dr, dc):
        """
        Evaluate consecutive pieces in a specific direction
        
        Args:
            board: 2D list representing game state
            player: ID of player to evaluate
            dr: Row direction (0 or 1)
            dc: Column direction (-1, 0, or 1)
            
        Returns:
            int: Score contribution from direction patterns
        """
        score = 0
        opponent = 3 - player
        
        for r in range(self.rows):
            for c in range(self.cols):
                # Check consecutive pieces in this direction
                count_player = 0
                count_empty = 0
                count_opponent = 0
                
                for i in range(4):
                    nr, nc = r + i * dr, c + i * dc
                    if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                        break
                        
                    if board[nr][nc] == player:
                        count_player += 1
                    elif board[nr][nc] == 0:
                        count_empty += 1
                    else:
                        count_opponent += 1
                else:
                    # Only evaluate if we have exactly 4 cells in a row
                    if count_opponent == 0:
                        # Score based on number of player pieces
                        if count_player == 4:
                            score += 10000
                        elif count_player == 3:
                            score += 100
                        elif count_player == 2:
                            score += 10
                    elif count_player == 0:
                        # Penalize opponent's potential wins
                        if count_opponent == 3 and count_empty == 1:
                            score -= 500
                        elif count_opponent == 2 and count_empty == 2:
                            score -= 10
                            
        return score

    def get_winner(self, board):
        """
        Check for winning player in current board state
        
        Args:
            board: 2D list representing game state
            
        Returns:
            int: Player ID of winner (1 or 2), or 0 if no winner
        """
        # Check horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if (board[r][c] != 0 and
                    board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]):
                    return board[r][c]
        
        # Check vertical
        for r in range(self.rows - 3):
            for c in range(self.cols):
                if (board[r][c] != 0 and
                    board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]):
                    return board[r][c]
        
        # Check diagonal /
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if (board[r][c] != 0 and
                    board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]):
                    return board[r][c]
        
        # Check diagonal \
        for r in range(self.rows - 3):
            for c in range(3, self.cols):
                if (board[r][c] != 0 and
                    board[r][c] == board[r+1][c-1] == board[r+2][c-2] == board[r+3][c-3]):
                    return board[r][c]
        
        return 0  # No winner

    def is_board_full(self, board):
        """
        Check if board has no empty positions
        
        Args:
            board: 2D list representing game state
            
        Returns:
            bool: True if board is full, False otherwise
        """
        return all(cell != 0 for row in board for cell in row)

    def get_next_open_row(self, col):
        """
        Find lowest empty row in specified column (instance board)
        
        Args:
            col: Column index to check
            
        Returns:
            int: Row index of first empty cell, or None if full
        """
        return self.get_next_open_row_from_board(self.board, col)

    def get_next_open_row_from_board(self, board, col):
        """
        Find lowest empty row in specified column (arbitrary board)
        
        Args:
            board: 2D list representing game state
            col: Column index to check
            
        Returns:
            int: Row index of first empty cell, or None if full
        """
        for r in range(self.rows-1, -1, -1):
            if board[r][col] == 0:
                return r
        return None

    def get_valid_moves_from_board(self, board):
        """
        Identify playable columns for given board state
        
        Args:
            board: 2D list representing game state
            
        Returns:
            list: Column indices with at least one empty position
        """
        return [c for c in range(self.cols) if board[0][c] == 0]