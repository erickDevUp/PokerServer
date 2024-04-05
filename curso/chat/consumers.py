import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .game import Game

PokerGame= Game()
class GameConsumer(WebsocketConsumer): 
    
    def connect(self):
        self.getId =self.channel_name
        print('ws connected')
        self.id = self.scope['url_route']['kwargs']['room_id']
        async_to_sync(self.channel_layer.group_add)(self.id, self.channel_name)
       
        
        print("room_id",self.id)
        print("channelName",self.channel_name)
        print(self.channel_layer.group_add)
       
        self.accept()
        PokerGame.get_id(self.id)
        PokerGame.add_player_to_game(self.getId,{"id":self.getId,"name":"", "money": 1000, "cards": PokerGame.create_new_hand()})
        PokerGame.create_new_game_turn(self.getId)
        PokerGame.create_new_game_board()
        
        self.send(json.dumps({"info":PokerGame.get_game_info(),"yourID":self.getId}))
        
        async_to_sync(self.channel_layer.group_send)(
            self.id, # El nombre del grupo, que en este caso es el room_id
            {
                "type": "newuseradd",
                "info": PokerGame.get_game_info(),
                "user": self.getId
            }
        )

        
    def disconnect(self, code):
        print('ws disconnect')
        PokerGame.remove_player_from_game(self.getId)
        async_to_sync(self.channel_layer.group_discard)(self.id, self.channel_name)
    
    def receive(self, text_data):
        print('ws recive')
        
        userSender = self.getId
        print(userSender)
        text_data_json = json.loads(text_data)
        
        if 'change_name' in text_data_json:
            new_name = text_data_json['new_name']
            PokerGame.change_player_name(userSender, new_name)
            print(PokerGame.get_game_info())
            async_to_sync(self.channel_layer.group_send)(
                self.id, # El nombre del grupo, que en este caso es el room_id
                {
                    'type': 'game.changename',
                    'message': new_name,
                }
            )

        try:
            data= json.loads(text_data)
            message = data['message']
            print(message)
            #get the id of the user whe send the message
            if userSender:
                async_to_sync(self.channel_layer.group_send)(
                    self.id,
                    {
                        'type':"game",
                        'message':message,
                        'islog':True,
                        'senderid_Channel':self.channel_name,
                        'userSender':userSender
                    
                    }
                
                )
            
        except json.JSONDecodeError as e:
            print("err json decoder",e)
        except Exception as e:
            print("err",e)
            
    def game(self, event):
        message = event['message']
        islog = event['islog']
        senderid = event['senderid_Channel']
        userSender= event['userSender']
        current_id = self.getId
        print(current_id,">>>>>>>",userSender)
        if current_id != userSender:
            self.send(text_data=json.dumps({
                'message':message,
                'islog':islog,
            }))
            
    def newuseradd(self, event):
        info = event['info']
        userSender= event['user']
        current_id = self.getId
        print(current_id,">>>>>>>",userSender)
        if current_id != userSender:
            self.send(text_data=json.dumps({
                'info':info,
            }))
    
    def game_changename(self, event):
        # Este método se llama cuando se recibe un mensaje del tipo 'game.message'
        message = event['message']
        # Aquí puedes enviar el mensaje a todos los usuarios conectados
        self.send(text_data=json.dumps({
            'newName': message,
            'newData': PokerGame.get_game_info()
        }))
        
    