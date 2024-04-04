import json
import redis
from deuces import Card, Deck, Evaluator

r = redis.Redis(
  host='redis-10847.c12.us-east-1-4.ec2.cloud.redislabs.com',
  port=10847,
  password='BW9TAMyWMSYec1LQU48UdKIHh5wyMYq2')

print(r.ping())


class Game:
    def __init__(self, id):
        self.id = id
        self.deck = Deck()

    def get_rank_class(self, board, player_hand):
        evaluator = Evaluator()
        p_score = evaluator.evaluate(board, player_hand)
        p_class = evaluator.get_rank_class(p_score)
        p_game = evaluator.class_to_string(p_class)
        return p_game

    def is_board_empty(self):
        board_json = r.hget(self.id, "board")
        if board_json is None:
            return True
        self.board = json.loads(board_json.decode('utf-8'))
        return len(self.board) == 0

    def pretty_print_cards(self, cards):
        # Optimización: Uso de comprensión de listas para mejorar la legibilidad.
        return [Card.int_to_pretty_str(card) for card in cards]

    def create_new_hand(self):
        return self.pretty_print_cards(self.deck.draw(2))

    def create_new_game_turn(self, player_id):
        self.turn = player_id
        r.hset(self.id, "turn", self.turn)
        r.rpush(f"{self.id}:players", player_id)
        r.hset(self.id, "rounds", 1)

    def create_new_game_board(self):
        if not self.is_board_empty():
            self.board = self.deck.draw(5)
            r.hset(self.id, "board", json.dumps(self.board))

    def add_player_to_game(self, player_id, player_info):
        # Mejora: Verifica si el conjunto de jugadores existe antes de intentar agregar.
        if not r.exists(f"{self.id}:players"):
            r.sadd(f"{self.id}:players", player_id)
        else:
            r.sadd(f"{self.id}:players", player_id)

        r.hset(self.id, player_id, json.dumps(player_info))

    def change_turn(self):
        players = r.lrange(f"{self.id}:players", 0, -1)
        players = [player.decode('utf-8') for player in players]
        current_turn = r.hget(self.id, "turn").decode('utf-8')
        current_turn_index = players.index(current_turn)
        next_turn_index = (current_turn_index + 1) % len(players)
        next_turn = players[next_turn_index]
        self.turn = next_turn
        r.hset(self.id, "turn", self.turn)
        if next_turn_index == 0:
            rounds = r.hget(self.id, "rounds").decode('utf-8')
            rounds = int(rounds) + 1 if rounds else 1
            self.rounds = rounds
            r.hset(self.id, "rounds", self.rounds)
            if self.rounds >= 4:
                self.reset_game()

    def get_game_info(self):
        board_data = r.hget(self.id, "board")
        if board_data is not None:
            self.board = json.loads(board_data.decode('utf-8'))
        else:
            self.board = None

        self.turn = r.hget(self.id, "turn").decode('utf-8') if r.hget(self.id, "turn") is not None else None

        players = r.lrange(f"{self.id}:players", 0, -1)
        player_info = {}
        for player_id in players:
            player_id = player_id.decode('utf-8')
            player_data = r.hget(self.id, player_id)
            if player_data is not None:
                player_info[player_id] = json.loads(player_data.decode('utf-8'))
            else:
                player_info[player_id] = None

        return {
            "board": self.board,
            "turn": self.turn,
            "players": player_info
        }

    def delete_game_session(self):
        players = r.lrange(f"{self.id}:players", 0, -1)
        r.delete(self.id)
        r.delete(f"{self.id}:players")
        for player_id in players:
            player_id = player_id.decode('utf-8')
            r.delete(f"{self.id}:{player_id}")

    def reset_game(self):
        self.create_new_game_board()
        players = r.lrange(f"{self.id}:players", 0, -1)
        for player in players:
            player = player.decode('utf-8')
            player_info = json.loads(r.hget(self.id, player).decode('utf-8'))
            player_info['cards'] = self.create_new_hand()
            r.hset(self.id, player, json.dumps(player_info))
        self.rounds = 1
        r.hset(self.id, "rounds", self.rounds)

    def __init__(self, id):
        self.id = id
        self.deck = Deck()

    def get_rank_class(self, board, player_hand):
        evaluator = Evaluator()
        p_score = evaluator.evaluate(board, player_hand)
        p_class = evaluator.get_rank_class(p_score)
        p_game = evaluator.class_to_string(p_class)
        return p_game

    def is_board_empty(self):
        board_json = r.hget(self.id, "board")
        if board_json is None:
            return True
        self.board = json.loads(board_json.decode('utf-8'))
        return len(self.board) == 0

    def pretty_print_cards(self, cards):
        handPrettier = []
        for card in cards:
            handPrettier.append(Card.int_to_pretty_str(card))
        return handPrettier

    def create_new_hand(self):
        return self.pretty_print_cards(self.deck.draw(2))

    def create_new_game_turn(self, player_id):
        self.turn = player_id
        r.hset(self.id, "turn", self.turn)
        r.rpush(f"{self.id}:players", player_id)
        r.hset(self.id, "rounds", 1)

    def create_new_game_board(self):
        if self.is_board_empty():
            return
        self.board = self.deck.draw(5)
        r.hset(self.id, "board", json.dumps(self.board))

    def add_player_to_game(self, player_id, player_info):
        # Verifica si el conjunto de jugadores existe y es del tipo correcto
        if not r.exists(f"{self.id}:players") or r.type(f"{self.id}:players") != 'set':
        # Si no existe o no es un conjunto, inicializa el conjunto
            r.delete(f"{self.id}:players") # Elimina la clave si ya existe pero es de otro tipo
            r.sadd(f"{self.id}:players", player_id) # Ahora es seguro agregar el jugador
        else:
        # Si el conjunto ya existe, simplemente agrega el jugador
            r.sadd(f"{self.id}:players", player_id)

        # Almacena la información del jugador
        r.hset(self.id, player_id, json.dumps(player_info))


    def change_turn(self):
        players = r.lrange(f"{self.id}:players", 0, -1)
        players = [player.decode('utf-8') for player in players]
        current_turn = r.hget(self.id, "turn").decode('utf-8')
        current_turn_index = players.index(current_turn)
        next_turn_index = (current_turn_index + 1) % len(players)
        next_turn = players[next_turn_index]
        self.turn = next_turn
        r.hset(self.id, "turn", self.turn)
        if next_turn_index == 0:
            rounds = r.hget(self.id, "rounds").decode('utf-8')
            rounds = int(rounds) + 1 if rounds else 1
            self.rounds = rounds
            r.hset(self.id, "rounds", self.rounds)
            if self.rounds >= 4:
                self.reset_game()

    def get_game_info(self):
        board_data = r.hget(self.id, "board")
        if board_data is not None:
            self.board = json.loads(board_data.decode('utf-8'))
        else:
            self.board = None # Or any default value you prefer

        self.turn = r.hget(self.id, "turn").decode('utf-8') if r.hget(self.id, "turn") is not None else None

        players = r.lrange(f"{self.id}:players", 0, -1)
        player_info = {}
        for player_id in players:
            player_id = player_id.decode('utf-8')
            player_data = r.hget(self.id, player_id)
            if player_data is not None:
                player_info[player_id] = json.loads(player_data.decode('utf-8'))
            else:
                player_info[player_id] = None # Or any default value you prefer

        return {
            "board": self.board,
            "turn": self.turn,
            "players": player_info
        }

    def delete_game_session(self):
        players = r.lrange(f"{self.id}:players", 0, -1)
        r.delete(self.id)
        r.delete(f"{self.id}:players")
        for player_id in players:
            player_id = player_id.decode('utf-8')
            r.delete(f"{self.id}:{player_id}")

    def reset_game(self):
        self.create_new_game_board()
        players = r.lrange(f"{self.id}:players", 0, -1)
        for player in players:
            player = player.decode('utf-8')
            player_info = json.loads(r.hget(self.id, player).decode('utf-8'))
            player_info['cards'] = self.create_new_hand()
            r.hset(self.id, player, json.dumps(player_info))
        self.rounds = 1
        r.hset(self.id, "rounds", self.rounds)