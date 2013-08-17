import logging
import json
import django

from socketio.namespace import BaseNamespace

from arcade.mixins import RoomsMixin, BroadcastMixin
from arcade.sdjango import namespace
from arcade.models import Player, Room, Game
from .models import StateOfNatureVo, PlayerVo


@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
	nicknames = []

	def initialize(self):
		self.logger = logging.getLogger("socketio.chat")
		self.log("Socketio session started")
        
	def log(self, message):
		self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
	def recv_disconnect(self):
		# Remove nickname from the list.
		self.log('Disconnected')
		self.disconnect(silent=True)
		return True

	# ========= GAME DEFINED EVENTS ===========
    
	def on_join(self, room_id, nickname):
		self.room = room_id
		self.join(room_id)
		self.set_nickname(nickname)
		return True

	def set_nickname(self, nickname):
		self.log('Nickname: {0}'.format(nickname))
		if not (nickname in self.nicknames):
			self.nicknames.append(nickname)
		self.socket.session['nickname'] = nickname
		self.broadcast_event('announcement', '%s has connected' % nickname)
		self.broadcast_event('nicknames', self.nicknames)    

	def on_user_message(self, msg):
		self.log('User message: {0}'.format(msg))
		self.emit_to_room(self.room, 'msg_to_room', self.socket.session['nickname'], msg)
		return True


@namespace('/playpolitics')
class PlaypoliticsNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

	def initialize(self):
		self.logger = logging.getLogger("socketio.playpolitics")
		self.log("Socketio session started")
    	

	def log(self, message):
		self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    

	def recv_disconnect(self):
		# Remove nickname from the list.
		self.log('Disconnected')
		self.disconnect(silent=True)
		return True


	def on_enter_zone(self):				
		self.emit('enter_zone', self._get_rooms())


	def on_create_room(self, room_name):
		print("roomname %s" % room_name)
		room, created = Room.objects.get_or_create(name=room_name)		
		self.broadcast_event('room_created', self._get_rooms())


	def on_join_room(self, room_id, user_id, nickname):		
		room = Room.objects.get(pk=room_id)
		user = django.contrib.auth.get_user_model().objects.get(pk=user_id)
		player, created = Player.objects.get_or_create(user=user, nickname=nickname)

		room.players.add(player)

		self.room = room_id
		self.join(self.room)
		self.emit('joined_room')
		self.broadcast_event('room_created', self._get_rooms())  #broadcast to others...


	def on_create_game(self):
		room = Room.objects.get(pk=self.room)
		game, created = Game.objects.get_or_create(room=room, type='stateofnature')			
		
		if created:		
			son = StateOfNatureVo(room.players.all())			
			game.json = son.to_json()
			game.save()

		self.emit_to_all_in_room(self.room, 'join_me')	

		
	def on_join_game(self):
		room = Room.objects.get(pk=self.room)
		game = Game.objects.get(room=room, type='stateofnature')			

		self.game = game.id

		son = StateOfNatureVo()
		son.from_json(game.json)
			
		if son.is_game_completed():			
			self.goto_next_round_if_needed(son)  #emits endgame message
			return
		else:				
			self.emit('begin_game', son.to_json())  # send just to this particular client, not everyone...


	def on_invest(self, player):
		son = self.load_game()
		if not self.can_player_go(player, son):
			print "ERROR: NOT YOUR TURN!"
			return
			
		son.invest(player)
		self.save_game(son)

		self.emit_to_all_in_room(self.room, 'invest', son.to_json())
		self.goto_next_round_if_needed(son)
			

	def on_attack(self, attacker, defender):
		son = self.load_game()
		if not self.can_player_go(attacker, son):
			print "ERROR: NOT YOUR TURN!"
			return
		if not son._can_attack(attacker, defender):
			print "ERROR: YOU CAN't ATTACK!"
			return

		son.attack(attacker, defender)
		self.save_game(son)

		self.emit_to_all_in_room(self.room, 'attack', son.to_json())
		self.goto_next_round_if_needed(son)



	def on_give(self, giver, receiver, amount):
		amount = int(amount)
		son = self.load_game()
		if not self.can_player_go(giver, son):
			print "ERROR: NOT YOUR TURN!"
			return
		if not son._can_give(giver, amount, receiver):
			print "ERROR: %s CANT GIVE %s TO %s!" % (giver, amount, receiver)
			return

		son.give(giver, amount, receiver)
		self.save_game(son)

		self.emit_to_all_in_room(self.room, 'give', son.to_json())
		self.goto_next_round_if_needed(son)


	def on_enslave(self, slavePlayer, masterPlayer):
		son = self.load_game()
		if not self.can_player_go(attacker, son):
			print "NOT YOUR TURN!"
			return

		son.enslave(slavePlayer, masterPlayer)
		self.save_game(son)

		self.emit_to_all_in_room(self.room, 'enslave', son.to_json())
		self.goto_next_round_if_needed(son)

	# ------------------------
	# helper methods
	# ------------------------

	def load_game(self):		
		game = Game.objects.get(id=self.game)
		son = StateOfNatureVo()
		son.from_json(game.json)
		return son


	def save_game(self, son):
		game = Game.objects.get(id=self.game)
		game.json = son.to_json()
		game.save()


	def can_player_go(self, player, stateofnature):
		"""
		Check if get a message from a player and it's not their turn.
		Check if game is over, and ignore message if so.
		"""
		if player != stateofnature.active_player:
			return False
		if stateofnature.is_game_completed():
			return False
		return True
	

	def goto_next_round_if_needed(self, stateofnature):		
		if stateofnature.is_game_completed():
			#create end of game message
			self.emit_to_all_in_room(self.room, 'end_game',  stateofnature.to_json())
			return

	def _get_rooms(self):
		rooms = []
		for room in Room.objects.all():
			r = dict()
			r['name'] 		= room.name
			r['id'] 		= room.id
			r['players']	= [player.nickname for player in room.players.all()]
			rooms.append(r)
		return rooms
