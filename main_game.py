import json
import os
from pathlib import Path
from Connect_4 import Connect4
from heuristic_bot import HeuristicBot
from adversarial_bot import AdversarialBot
import time
from collections import defaultdict

# Player Implementations
def human_player(game):
    """
    Handles human player input for Connect 4 moves
    
    Args:
        game: Connect4 game instance
        
    Returns:
        int: Column number selected by human player
        
    Behavior:
        - Continuously prompts until valid move entered
        - Validates input is numeric and within valid columns
        - Shows available columns in prompt
    """
    valid_moves = game.get_valid_moves()
    while True:
        try:
            col = int(input(f"Enter column (0-{game.cols-1}): "))
            if col in valid_moves:
                return col
            print("Invalid move. Try again.")
        except ValueError:
            print("Please enter a valid number.")

def heuristic_bot_player(game_state):
    """
    Basic heuristic AI player implementation
    
    Args:
        game_state: Current Connect4 game instance
        
    Returns:
        int: Column number selected by heuristic bot
        
    Note:
        Uses static evaluation function without visualization
    """
    board = game_state.board.tolist()
    bot = HeuristicBot(
        board=board,
        current_player=game_state.current_player,
        valid_moves=game_state.get_valid_moves(),
        move_number=len(game_state.moves_history) + 1,
        player_type="heuristic_bot"
    )
    return bot.make_best_move()

def dynamic_heuristic_bot_player(game_state):
    """
    Enhanced heuristic AI with dynamic weights and visualization
    
    Args:
        game_state: Current Connect4 game instance
        
    Returns:
        tuple: (column_number, visualization_data)
        
    Features:
        - Adaptive scoring based on board state
        - Potential move visualization
    """
    board = game_state.board.tolist()
    bot = HeuristicBot(
        board=board,
        current_player=game_state.current_player,
        valid_moves=game_state.get_valid_moves(),
        move_number=len(game_state.moves_history) + 1,
        player_type="dynamic_heuristic_bot",
        use_dynamic_weights=True
    )
    return bot.make_best_move()

def adversarial_bot_player(game_state):
    """
    Minimax-based AI with alpha-beta pruning
    
    Args:
        game_state: Current Connect4 game instance
        
    Returns:
        int: Column number selected by adversarial bot
        
    Configuration:
        - Search depth configurable via depth parameter
        - Uses alpha-beta pruning for efficiency
    """
    board = game_state.board.tolist()
    bot = AdversarialBot(
        board=board,
        current_player=game_state.current_player,
        valid_moves=game_state.get_valid_moves(),
        move_number=len(game_state.moves_history) + 1,
        player_type="adversarial_bot",
        depth=3  # Adjust depth as needed
    )
    return bot.make_best_move()

# Game Utilities
def save_game_state(game, game_id, player_type, move_number):
    """
    Saves complete game state to JSON file
    
    Args:
        game: Connect4 game instance
        game_id: Unique identifier for the game
        player_type: Type of player making next move
        move_number: Current move sequence number
        
    Returns:
        Path: Filepath where state was saved
        
    File Structure:
        games/{game_id}/{player_type}/state_{move_number}.json
    """
    base_dir = Path(f"games/{game_id}")
    player_label = f"Human_{'X' if game.current_player == 1 else 'O'}" if player_type == "human" else player_type
    save_dir = base_dir / player_label
    save_dir.mkdir(parents=True, exist_ok=True)

    state_path = save_dir / f"state_{move_number}.json"
    with open(state_path, 'w') as f:
        json.dump({
            "board": game.board.tolist(),
            "current_player": game.current_player,
            "valid_moves": game.get_valid_moves(),
            "move_number": move_number,
            "player_type": player_label
        }, f)

    return state_path

def save_move(game_id, player_type, move_number, move, current_player):
    """
    Records individual move to JSON file
    
    Args:
        game_id: Unique identifier for the game
        player_type: Type of player making move
        move_number: Move sequence number
        move: Column number played
        current_player: Player ID (1 or 2)
        
    Returns:
        Path: Filepath where move was saved
        
    File Structure:
        games/{game_id}/{player_type}/move_{move_number}.json
    """
    base_dir = Path(f"games/{game_id}")
    player_label = f"Human_{'X' if current_player == 1 else 'O'}" if player_type == "human" else player_type
    save_dir = base_dir / player_label
    save_dir.mkdir(parents=True, exist_ok=True)

    move_path = save_dir / f"move_{move_number}.json"
    with open(move_path, 'w') as f:
        json.dump({
            "move": move,
            "move_number": move_number,
            "player_type": player_type,
            "player_symbol": "X" if current_player == 1 else "O"
        }, f)

    return move_path

def get_next_game_id():
    """
    Generates sequential game ID by scanning existing games
    
    Returns:
        str: Formatted game ID (e.g., "game_001")
        
    Behavior:
        - Creates games directory if missing
        - Scans for existing game_* folders
        - Returns next available sequential ID
    """
    games_dir = Path("games")
    games_dir.mkdir(exist_ok=True)
    
    existing_ids = []
    for d in games_dir.iterdir():
        if d.is_dir() and d.name.startswith("game_"):
            try:
                num = int(d.name.split("_")[1])
                existing_ids.append(num)
            except (ValueError, IndexError):
                continue
    
    next_id = max(existing_ids) + 1 if existing_ids else 1
    return f"game_{next_id:03d}"

def clear_terminal():
    """
    Clears terminal screen in platform-agnostic way
    
    Supports:
        - Windows (cls)
        - Unix/Mac (clear)
    """
    os.system('cls' if os.name == 'nt' else 'clear')

# Main Game Loop
def play_game_with_storage(game_id=None, player1_type="human", player2_type="human"):
    """
    Main game loop with automatic state saving
    
    Args:
        game_id: Optional custom game identifier
        player1_type: Type of player 1 (human/heuristic_bot/etc)
        player2_type: Type of player 2 (human/heuristic_bot/etc)
        
    Returns:
        int: Winning player ID (None if draw)
        
    Features:
        - Saves state before each move
        - Records all moves to files
        - Saves final result
        - Supports mixed human/AI gameplay
    """
    if game_id is None:
        game_id = get_next_game_id()

    game = Connect4()
    player_types = {1: player1_type, 2: player2_type}
    move_number = 0

    while not game.game_over:
        clear_terminal()
        game.display()

        current_player = game.current_player
        current_player_type = player_types[current_player]
        move_number += 1

        save_game_state(game, game_id, current_player_type, move_number)

        if current_player_type == "human":
            col = human_player(game)
        elif current_player_type == "dynamic_heuristic_bot":
            col = dynamic_heuristic_bot_player(game)
            clear_terminal()
            game.display()
        elif current_player_type == "heuristic_bot":
            col = heuristic_bot_player(game)
        elif current_player_type == "adversarial_bot":
            col = adversarial_bot_player(game)
        else:
            col = 0  # Default for unimplemented bots

        if col is None:
            break

        save_move(game_id, current_player_type, move_number, col, current_player)
        game.drop_piece(col)

    # Final display
    clear_terminal()
    game.display()
    print("\nGame Over!")

    # Save result
    result_path = Path(f"games/{game_id}") / "result.json"
    with open(result_path, 'w') as f:
        json.dump({
            "winner": game.winner,
            "total_moves": move_number,
            "player1_type": player1_type,
            "player2_type": player2_type
        }, f)

    return game.winner

# Extracting stats from bot vs bot testing for Results section in report
def run_bot_vs_bot_tournament(bot1_type, bot2_type, num_games=100, display_progress=True):
    """
    Run a tournament between two AI bots and collect detailed statistics
    
    Args:
        bot1_type (str): Type of first bot ('heuristic_bot' or 'adversarial_bot')
        bot2_type (str): Type of second bot ('heuristic_bot' or 'adversarial_bot')
        num_games (int): Number of games to play
        display_progress (bool): Whether to show progress during tournament
    
    Returns:
        dict: Comprehensive statistics including win rates, move counts, and game durations
    """
    # Initialize statistics
    stats = {
        'total_games': num_games,
        'bot1_wins': 0,
        'bot2_wins': 0,
        'draws': 0,
        'move_counts': [],
        'durations': [],
        'winning_moves': defaultdict(int),
        'player1_start_advantage': 0,
        'early_wins': {'bot1': 0, 'bot2': 0, 'draw': 0},  # Games ending before 20 moves
        'mid_wins': {'bot1': 0, 'bot2': 0, 'draw': 0},    # Games ending between 20-35 moves
        'late_wins': {'bot1': 0, 'bot2': 0, 'draw': 0},   # Games ending after 35 moves
        'bot1_type': bot1_type,
        'bot2_type': bot2_type
    }

    if display_progress:
        print(f"Starting {num_games} game tournament between {bot1_type} (Player 1) vs {bot2_type} (Player 2)")
        print("=" * 60)

    for game_num in range(1, num_games + 1):
        # Alternate starting player every game to remove bias
        if game_num % 2 == 0:
            player1_type, player2_type = bot2_type, bot1_type
            swapped = True
        else:
            player1_type, player2_type = bot1_type, bot2_type
            swapped = False

        game = Connect4()
        start_time = time.time()
        move_count = 0

        while not game.game_over:
            move_count += 1
            current_player = game.current_player
            valid_moves = game.get_valid_moves()

            if current_player == 1:
                bot_type = player1_type
            else:
                bot_type = player2_type

            # Get bot move based on type
            if bot_type == 'heuristic_bot':
                bot = HeuristicBot(
                    board=game.board.tolist(),
                    current_player=current_player,
                    valid_moves=valid_moves,
                    move_number=move_count,
                    player_type=bot_type
                )
                col = bot.make_best_move()
            elif bot_type == 'dynamic_heuristic_bot':
                bot = HeuristicBot(
                    board=game.board.tolist(),
                    current_player=current_player,
                    valid_moves=valid_moves,
                    move_number=move_count,
                    player_type=bot_type,
                    use_dynamic_weights=True
                )
                col = bot.make_best_move()
            elif bot_type == 'adversarial_bot':
                bot = AdversarialBot(
                    board=game.board.tolist(),
                    current_player=current_player,
                    valid_moves=valid_moves,
                    move_number=move_count,
                    player_type=bot_type,
                    depth=5
                )
                col = bot.make_best_move()
            else:
                raise ValueError(f"Unknown bot type: {bot_type}")

            game.drop_piece(col)

        # Record game results
        duration = time.time() - start_time
        stats['move_counts'].append(move_count)
        stats['durations'].append(duration)

        if swapped:
            # Results need to be inverted since we swapped players
            if game.winner == 1:
                winner = bot2_type
                stats['bot2_wins'] += 1
            elif game.winner == 2:
                winner = bot1_type
                stats['bot1_wins'] += 1
            else:
                winner = 'draw'
                stats['draws'] += 1
        else:
            if game.winner == 1:
                winner = bot1_type
                stats['bot1_wins'] += 1
            elif game.winner == 2:
                winner = bot2_type
                stats['bot2_wins'] += 1
            else:
                winner = 'draw'
                stats['draws'] += 1

        # Record winning move if applicable
        if game.winner is not None:
            stats['winning_moves'][game.moves_history[-1]] += 1

        # Track game phase statistics
        if move_count < 20:
            phase = 'early_wins'
        elif move_count < 35:
            phase = 'mid_wins'
        else:
            phase = 'late_wins'
        
        if winner == bot1_type:
            stats[phase]['bot1'] += 1
        elif winner == bot2_type:
            stats[phase]['bot2'] += 1
        else:
            stats[phase]['draw'] += 1

        # Track starting player advantage
        if not swapped and game.winner == 1:
            stats['player1_start_advantage'] += 1
        elif swapped and game.winner == 1:
            stats['player1_start_advantage'] += 1

        if display_progress and (game_num % 10 == 0 or game_num == num_games):
            print(f"Game {game_num}/{num_games} completed.")

    # Calculate derived statistics
    stats['bot1_win_rate'] = stats['bot1_wins'] / num_games * 100
    stats['bot2_win_rate'] = stats['bot2_wins'] / num_games * 100
    stats['draw_rate'] = stats['draws'] / num_games * 100
    stats['avg_moves'] = sum(stats['move_counts']) / num_games
    stats['avg_duration'] = sum(stats['durations']) / num_games
    stats['player1_start_advantage'] = stats['player1_start_advantage'] / num_games * 100

    return stats

def print_tournament_results(stats):
    """Display formatted tournament results"""
    print("\n" + "=" * 60)
    print(f"TOURNAMENT RESULTS: {stats['bot1_type']} vs {stats['bot2_type']}")
    print("=" * 60)
    print(f"Total Games: {stats['total_games']}")
    print(f"{stats['bot1_type']} Wins: {stats['bot1_wins']} ({stats['bot1_win_rate']:.1f}%)")
    print(f"{stats['bot2_type']} Wins: {stats['bot2_wins']} ({stats['bot2_win_rate']:.1f}%)")
    print(f"Draws: {stats['draws']} ({stats['draw_rate']:.1f}%)")
    print(f"\nAverage Moves per Game: {stats['avg_moves']:.1f}")
    print(f"Average Game Duration: {stats['avg_duration']:.2f} seconds")
    print(f"Player 1 Starting Advantage: {stats['player1_start_advantage']:.1f}%")
    print("\nWin Distribution by Game Phase:")
    print(f"Early Game (<20 moves): {stats['bot1_type']} {stats['early_wins']['bot1']} | "
          f"{stats['bot2_type']} {stats['early_wins']['bot2']} | "
          f"Draws {stats['early_wins']['draw']}")
    print(f"Mid Game (20-35 moves): {stats['bot1_type']} {stats['mid_wins']['bot1']} | "
          f"{stats['bot2_type']} {stats['mid_wins']['bot2']} | "
          f"Draws {stats['mid_wins']['draw']}")
    print(f"Late Game (>35 moves): {stats['bot1_type']} {stats['late_wins']['bot1']} | "
          f"{stats['bot2_type']} {stats['late_wins']['bot2']} | "
          f"Draws {stats['late_wins']['draw']}")

# # Bulk Run
# # Run bot vs bot matches multiple times
# if __name__ == "__main__":
#     tournament_stats = run_bot_vs_bot_tournament(
#         bot1_type='heuristic_bot',
#         bot2_type='heuristic_bot',
#         num_games=100,
#         display_progress=True
#     )
    
#     print_tournament_results(tournament_stats)

# Normal Game Mode
# Start the game
if __name__ == "__main__":
    """
    Default game configuration when run directly
    
    Starts a game with:
    - Player 1: *
    - Player 2: *
    """
    play_game_with_storage(player1_type="human", player2_type="dynamic_heuristic_bot")

