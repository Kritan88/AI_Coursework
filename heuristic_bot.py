class HeuristicBot:
    """AI player using heuristic evaluation"""
    def __init__(self, board, 
                 current_player, 
                 valid_moves, 
                 move_number, 
                 player_type, 
                 use_dynamic_weights=False):
        """
        Initialize heuristic-based bot player
        
        Args:
            board: 2D list representing game board state
            current_player: ID of current player (1 or 2)
            valid_moves: List of currently playable column indices
            move_number: Current move count in the game
            player_type: Player identification metadata
            use_dynamic_weights: Flag to enable adaptive scoring (default: False)
        """
        self.board = board
        self.current_player = current_player
        self.valid_moves = valid_moves
        self.move_number = move_number
        self.player_type = player_type
        self.use_dynamic_weights = use_dynamic_weights
        
        self.opponent = 3 - self.current_player
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.rows > 0 else 0

    def make_best_move(self):
        """
        Select optimal column based on heuristic scoring
        
        Returns:
            int: Column index of best move, or None if no valid moves
        """
        move_scores = self.compute_move_scores()
        if not move_scores:
            return None
        
        return max(move_scores, key=move_scores.get)

    def compute_move_scores(self):
        """
        Calculate heuristic scores for all valid moves
        
        Returns:
            dict: Mapping of column indices to their heuristic scores
        """
        move_scores = {}
        win_moves = self.find_winning_move()
        block_moves = self.find_opponent_winning_move()

        for col in self.valid_moves:
            row = next(r for r in range(self.rows-1, -1, -1) if self.board[r][col] == 0)
            
            if col in win_moves:
                move_scores[col] = float('inf')
            elif col in block_moves:
                move_scores[col] = 1000000
            else:
                self.board[row][col] = self.current_player
                my_3, my_2 = self.count_consecutive(self.current_player)
                opp_3, opp_2 = self.count_consecutive(self.opponent)
                self.board[row][col] = 0
                
                score = 0
                score += my_3 * 1000 + my_2 * 100
                score -= opp_3 * 1500 + opp_2 * 200
                score += self.get_positional_bonus(col, row)
                
                move_scores[col] = score
                
        return move_scores

    def get_positional_bonus(self, col, row):
        """
        Calculate positional advantages for a potential move
        
        Args:
            col: Column index being evaluated
            row: Row index where piece would land
        
        Returns:
            int: Calculated bonus score for board position
        """
        center = self.cols // 2
        bonus = (self.cols // 2 - abs(col - center)) * 3
        bonus += (self.rows - row) * 2
        
        if self.use_dynamic_weights:
            potentials = self.calculate_dynamic_weights()
            bonus += potentials.get(col, 0) * 2
            
            if self.move_number >= 15:
                bonus += potentials.get(col, 0) * 5
        else:
            if self.move_number < 15:
                bonus += (self.cols - abs(col - center))
            else:
                bonus += abs(col - center)
                
        return bonus
    
    def calculate_dynamic_weights(self):
        """
        Compute dynamic potential of columns for creating winning paths
        
        Returns:
            dict: Column indices mapped to their potential path counts
        """
        potentials = {}
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for col in self.valid_moves:
            row = next(r for r in range(self.rows-1, -1, -1) if self.board[r][col] == 0)
            total_count = 0
            
            for dx, dy in directions:
                for offset in range(-3, 1):
                    valid_segment = True
                    start_r = row + offset * dx
                    start_c = col + offset * dy
                    
                    for i in range(4):
                        r = start_r + i * dx
                        c = start_c + i * dy
                        
                        if not (0 <= r < self.rows and 0 <= c < self.cols):
                            valid_segment = False
                            break
                        
                        cell_value = self.board[r][c]
                        if r == row and c == col:
                            cell_value = self.current_player
                        
                        if cell_value == self.opponent:
                            valid_segment = False
                            break
                    
                    if valid_segment:
                        total_count += 1
            
            potentials[col] = total_count
        
        return potentials

    def count_consecutive(self, player):
        """
        Count consecutive pieces patterns for specified player
        
        Args:
            player: Player ID to evaluate (1 or 2)
            
        Returns:
            tuple: (count_3, count_2) where:
                count_3: Number of open-ended 3-in-a-row sequences
                count_2: Number of open-ended 2-in-a-row sequences
        """
        count_3 = count_2 = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != player:
                    continue
                    
                for dx, dy in directions:
                    if not (0 <= r + 3*dx < self.rows and 0 <= c + 3*dy < self.cols):
                        continue
                        
                    consecutive = 0
                    has_opponent = False
                    
                    for i in range(4):
                        cell = self.board[r + i*dx][c + i*dy]
                        if cell == player:
                            consecutive += 1
                        elif cell == 3 - player:
                            has_opponent = True
                            break
                    
                    if has_opponent or consecutive < 2:
                        continue
                    
                    start_open = (0 <= r - dx < self.rows and 0 <= c - dy < self.cols and 
                                 self.board[r - dx][c - dy] == 0)
                    end_open = (0 <= r + 4*dx < self.rows and 0 <= c + 4*dy < self.cols and 
                               self.board[r + 4*dx][c + 4*dy] == 0)
                    
                    if start_open or end_open:
                        if consecutive == 3:
                            count_3 += 1
                        elif consecutive == 2:
                            count_2 += 1
        
        return count_3, count_2

    def find_winning_move(self):
        """
        Identify immediate winning move for current player by checking all valid moves.
        If multiple winning moves exist, randomly selects one.
        
        Returns:
            int: Column index of a winning move, or None if none exists
        """
        winning_moves = self.get_winning_moves(self.current_player)
        
        return winning_moves

    def find_opponent_winning_move(self):
        """
        Identify opponent's winning move to block by checking all valid moves.
        If multiple winning moves exist for opponent, randomly selects one to block.
        
        Returns:
            int: Column index requiring block, or None if none exists
        """
        winning_moves = self.get_winning_moves(self.opponent)
    
        return winning_moves

    def get_winning_moves(self, player):
        board = self.board
        valid_moves = self.valid_moves

        rows = len(board)
        if rows == 0:
            cols = 0
        else:
            cols = len(board[0])
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        winning_moves = []
        
        for col in valid_moves:
            row = -1
            for r in range(rows-1, -1, -1):
                if board[r][col] == 0:
                    row = r
                    break
                    
            if row == -1:
                continue
                
            for dx, dy in directions:
                count = 1
                
                r_temp, c_temp = row + dx, col + dy
                while 0 <= r_temp < rows and 0 <= c_temp < cols and board[r_temp][c_temp] == player:
                    count += 1
                    r_temp += dx
                    c_temp += dy
                    
                r_temp, c_temp = row - dx, col - dy
                while 0 <= r_temp < rows and 0 <= c_temp < cols and board[r_temp][c_temp] == player:
                    count += 1
                    r_temp -= dx
                    c_temp -= dy
                    
                if count >= 4:
                    winning_moves.append(col)
            
        return winning_moves