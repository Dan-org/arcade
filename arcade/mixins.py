"""
These are general-purpose Mixins from https://github.com/abourget/gevent-socketio/blob/master/socketio/mixins.py

For use with Namespaces -- that are generally useful for most simple projects, e.g. Rooms, Broadcast.


"""
import logging
import json
import django

from socketio.namespace import BaseNamespace

from arcade.sdjango import namespace
from arcade.models import Player, Room, Game


class RoomsMixin(object):

	def __init__(self, *args, **kwargs):
		super(RoomsMixin, self).__init__(*args, **kwargs)
		if 'rooms' not in self.session:
			self.session['rooms'] = set() # a set of simple strings

	def join(self, room):
		"""Lets a user join a room on a specific Namespace."""
		self.session['rooms'].add(self._get_room_name(room))

	def leave(self, room):
		"""Lets a user leave a room on a specific Namespace."""
		self.session['rooms'].remove(self._get_room_name(room))

	def _get_room_name(self, room):
		return self.ns_name + '_' + room

	def _emit_to_room(self, room, event, including_me=True, *args):
		"""
		This is sent to all in the room (in this particular Namespace)
		@param not_me, if True, message won't be sent to room connected to this socket, 
		e.g., if you don't want to send chat message to yourself.
		"""
		pkt = dict(type="event", name=event, args=args, endpoint=self.ns_name)
		room_name = self._get_room_name(room)
		for sessid, socket in self.socket.server.sockets.iteritems():
			if 'rooms' not in socket.session:
				continue					
			if room_name in socket.session['rooms']:
				if (not including_me) and (self.socket == socket):
					continue
				else:
					socket.send_packet(pkt)

		# room_name = self._get_room_name(room)
		# for sessid, socket in self.socket.server.sockets.iteritems():
		# 	if 'rooms' not in socket.session:
		# 		continue					
		# 	if room_name in socket.session['rooms']:
		# 		if (not including_me) and (self.socket == socket):
		# 			continue
		# 		else:					
		# 			self.emit(event, args, kwargs)

	def emit_to_room(self, room, event, *args):
		"""This is sent to all in the room (in this particular Namespace)"""
		self._emit_to_room(room, event, False, *args)

	def emit_to_all_in_room(self, room, event, *args, **kwargs):
		"""This is sent to all in the room (in this particular Namespace) inlcluding this room"""
		self._emit_to_room(room, event, True, *args)


class BroadcastMixin(object):
		"""
		Mix in this class with your Namespace to have a broadcast event method.
		Use it like this:
		class MyNamespace(BaseNamespace, BroadcastMixin):
		def on_chatmsg(self, event):
		self.broadcast_event('chatmsg', event)
		"""
		def broadcast_event(self, event, *args):
			"""This is sent to all in the sockets in this particular Namespace, including itself. """
			pkt = dict(type="event", name=event, args=args, endpoint=self.ns_name)
			for sessid, socket in self.socket.server.sockets.iteritems():
				socket.send_packet(pkt)

		def broadcast_event_not_me(self, event, *args):
			""" This is sent to all in the sockets in this particular Namespace, except itself. """
			pkt = dict(type="event", name=event, args=args, endpoint=self.ns_name)

			for sessid, socket in self.socket.server.sockets.iteritems():
				if socket is not self.socket:
					socket.send_packet(pkt)




class LobbyMixin(BaseNamespace, RoomsMixin, BroadcastMixin):

	DIR_NAME = ""

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

	def on_enter_zone(self, user_id, nickname):
		""" Called after connection when client wants to play state of nature."""		
		
		user = django.contrib.auth.get_user_model().objects.get(pk=user_id)
		player, created = Player.objects.get_or_create(user=user, nickname=nickname)

		# shouldn't return all the rooms for state of nature, only open ones...		
		self.broadcast_event('rooms_changed')

	def on_create_room(self, room_name):
		""" 
		User tries to create a new state of nature game
		@param room_name as a string
		"""
		if (room_name == "")  or (room_name == None):
			print "ERROR: room name cannot be null in on_create_room"
			return

		game = Game.objects.get(dir=self.DIR_NAME)
		room, created = Room.objects.get_or_create(game=game, name=room_name)		
		
		self.broadcast_event('rooms_changed')

	def on_join_room(self, room_id, user_id):		
		room 	= Room.objects.get(pk=room_id)		
		user 	= django.contrib.auth.get_user_model().objects.get(pk=user_id)
		player 	= Player.objects.get(user=user)

		if room.status == "getting-ready":
			room.players.add(player)
		else:
			# can't join room if over or in-progress (should probably send error message)
			# only exception is if you're already in game (because maybe you got kicked out by browser...)
			if not (player in room.players.all()):
				return
		self.room = room_id
		self.join(self.room)
		self.emit('joined_room')
		self.broadcast_event('rooms_changed') #broadcast to others...		

	def on_send_room_list(self, user_id):
		user 	= django.contrib.auth.get_user_model().objects.get(pk=user_id)
		player 	= Player.objects.get(user=user)
		self.emit('room_info', self._get_rooms(game_dir=self.DIR_NAME, player=player))  #broadcast to others...

	def _get_rooms(self, game_dir, player):
		rooms = []
		game = Game.objects.get(dir=game_dir)
		for room in sorted(game.rooms.all(), key=self._sort_rooms):
			r = dict()
			r['name'] 			= room.name
			r['id'] 			= room.id		
			#r['min_players']	= room.game.min_players
			#r['max_players']	= room.game.max_players	
			r['status']			= room.status
			r['players']		= [aplayer.nickname for aplayer in room.players.all()]			

			if room.status == 'getting-ready':
				r['is_joinable'] = True
			else:				
				r['is_joinable'] = (player in room.players.all())

			rooms.append(r)
		return rooms

	def _sort_rooms(self, room):
		""" converts room status to a number for sorting. """
		return {
    		'getting-ready':0,
    		'in-progress':1,
    		'over':2}[room.status]




