"""
These are general-purpose Mixins from https://github.com/abourget/gevent-socketio/blob/master/socketio/mixins.py

For use with Namespaces -- that are generally useful for most simple projects, e.g. Rooms, Broadcast.


"""


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

