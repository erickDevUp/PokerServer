import json
from deuces import Card, Deck, Evaluator

class Game:
    def __init__(self):
        self.id = id
        self.deck = Deck()
        self.board = []
        self.turn = None
        self.rounds = 0
        self.players = {}

    def get_id(self,id):
        self.id = id
    
    def get_rank_class(self, board, player_hand):
        evaluator = Evaluator()
        p_score = evaluator.evaluate(board, player_hand)
        p_class = evaluator.get_rank_class(p_score)
        p_game = evaluator.class_to_string(p_class)
        return p_game

    def is_board_empty(self):
        return len(self.board) == 0

    def pretty_print_cards(self, cards):
        return [Card.int_to_pretty_str(card) for card in cards]

    def create_new_hand(self):
        return self.pretty_print_cards(self.deck.draw(2))

    def create_new_game_turn(self, player_id):
        self.turn = player_id
        self.rounds = 1

    def create_new_game_board(self):
        if not self.is_board_empty():
            return
        self.board = self.pretty_print_cards(self.deck.draw(5))

    def add_player_to_game(self, player_id, player_info):
        self.players[player_id] = player_info

    def change_turn(self):
        players = list(self.players.keys())
        current_turn_index = players.index(self.turn)
        next_turn_index = (current_turn_index + 1) % len(players)
        next_turn = players[next_turn_index]
        self.turn = next_turn
        if next_turn_index == 0:
            self.rounds += 1
            if self.rounds >= 4:
                self.reset_game()

    def get_game_info(self):
        return {
            "board": self.board,
            "turn": self.turn,
            "players": self.players
        }

    def delete_game_session(self):
        self.board = []
        self.turn = None
        self.rounds = 0
        self.players = {}

    def reset_game(self):
        self.create_new_game_board()
        for player_id in self.players:
            self.players[player_id]['cards'] = self.create_new_hand()
        self.rounds = 1

    def change_player_name(self, player_id, new_name):
       """
       Cambia el nombre de un jugador existente.

       :param player_id: El ID del jugador cuyo nombre se va a cambiar.
       :param new_name: El nuevo nombre para el jugador.
       """
       if player_id in self.players:
           self.players[player_id]['name'] = new_name
       else:
           print(f"No se encontró el jugador con ID: {player_id}")
