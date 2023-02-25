import chess

# init
DEPTH = 3
KING_POINTS = 20 # assume king = 20 points
piece_value = {1:1, 2:3, 3:3, 4:5, 5:8}
icon_lookup = {'r':'♜', 'n':'♞', 'b':'♝', 'q':'♛', 'k':'♚', 'p':'♟', 'R':'♖', 'N':'♘', 'B':'♗', 'Q':'♕', 'K':'♔', 'P':'♙'}
positional_value = {'e5': 0.2, 'd5': 0.2, 'e4': 0.2, 'd4': 0.2, 'f6': 0.1, 'e6': 0.1, 'd6': 0.1, 'c6': 0.1, 'c5': 0.1, 'c4': 0.1, 'c3': 0.1, 'f5': 0.1, 'f4': 0.1, 'f3': 0.1, 'e3': 0.1, 'd3': 0.1}
board = chess.Board()

def main():
    print('Enter moves in standard algebraic notation')
    # start: player white / bot black
    while (not(board.is_checkmate())):

        print(board_to_icons(board))
        print("\n")
        
        # player move
        while True:
            value = input("Move: ") #'Nf3' for example
            # value = 'Nf3'
            try:
                board.push(board.parse_san(value))
                break
            except:
                print("Invalid move.")
        
        # check for end
        if board.outcome() is not(None): break

        # bot move
        print(board_to_icons(board))
        print("\n")
        
        best_move = get_best_move()
        if best_move == None: break

        print(best_move)
        board.push(best_move)


    print(board_to_icons(board))
    if board.outcome().termination.name == 'STALEMATE':
        print("Stalemate")
    elif board.outcome().winner:
        print("White wins")
    else:
        print("Black wins")

def get_best_move():
    # go through all legal moves and rank by possible points recursively with depth n
    initial_possible_moves = {}

    for move in board.legal_moves:
        initial_possible_moves[move] = get_avg_points_for_move(move,DEPTH,True)

    maxPoints = max(initial_possible_moves.values())
    for move,points in initial_possible_moves.items():
        if points == maxPoints:
            best_move = move

    return best_move

# convert board to icons
def board_to_icons(board):
    display = list(str(board))
    for i in range(len(display)):
        if display[i] in list(icon_lookup.keys()):
            display[i] = icon_lookup[display[i]]
    
    return "".join(display)
        
def get_avg_points_for_move(move, depth, turn):
        # get points for current move
        destination = board.piece_type_at(move.to_square)
        if destination is None:
            points = 0
        else:
            points = piece_value[destination]

        # positional points, more points if close to center (1.2x the runtime)
        to_square = str(move)[2:4]
        if to_square in positional_value.keys():
            points += positional_value[to_square]
        
        # checks get more points (2x the runtime)
        if board.gives_check(move):
            points += 0.2
        
        # promotion adds points
        if move.promotion:
            points += piece_value[move.promotion]

        # if no depth
        if depth == 1:
            return points
        else:
            # make the move
            board.push(move)
            
            outcome = board.outcome()
            # check for end and unmake the move
            if outcome is not(None):
                # unmake the move
                board.pop()
                if outcome.termination.name == 'CHECKMATE':
                    return KING_POINTS
                else:
                    # stalemate will appear as bad as losing 3 points
                    return -3
            
            # get all possible moves
            possible_moves = {}
            
            for move in board.legal_moves:
                possible_moves[move] = get_avg_points_for_move(move, depth - 1, not(turn))

            # if some moves are SIGNIFICANTLY WORSE on depth1 then just remove them
            to_remove = []
            for move,val in possible_moves.items():
                if val < max(possible_moves.values()) - 3:
                    to_remove += [move]
            
            for move in to_remove:
                possible_moves.pop(move)

            # avg their points
            avg_points = sum(possible_moves.values())/len(possible_moves)
            
            # unmake the move
            board.pop()

            return points - avg_points

if __name__ == "__main__":
    main()