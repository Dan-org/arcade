from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
import jsonfield
import json
import sys

class Zone(models.Model):
	"""
	Zone is a collection of rooms.
	"""
	name = models.CharField(max_length=20)

	def __unicode__(self):
		return self.name


class Player(models.Model):
	"""
	Associates a user with a nickname to avoid custom user model issues.
	"""
	user 		= models.ForeignKey(settings.AUTH_USER_MODEL)
	nickname 	= models.CharField(max_length=24)


class Room(models.Model):
	"""
	Room is a collection of users that can chat and play a game.
	"""
	zone 	= models.ForeignKey(Zone, related_name="rooms")
	name 	= models.CharField(max_length=20)
	slug 	= models.SlugField(blank=True)    
	players = models.ManyToManyField(Player, blank=True, null=True, related_name="rooms_joined")
	is_open = models.BooleanField(default=True)

	class Meta:
		ordering = ("name",)

	def __unicode__(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ("room", (self.slug,))

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super(Room, self).save(*args, **kwargs)


class Game(models.Model):
	"""
	Stores data about a game.
	"""
	room 	= models.ForeignKey(Room, related_name="stateOfNatureGames")
	type	= models.CharField(max_length=20) 
	json	= jsonfield.JSONField()

	def __unicode__(self):
		return "Game type=%s room=%s" % (self.type, self.room.name)

	@models.permalink
	def get_absolute_url(self):
		return ("game", (str(self.id)))



# ------------------------------
#  STATE OF NATURE models
# ------------------------------

class StateOfNatureEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, StateOfNatureVo):
        	return obj.__dict__
        elif isinstance(obj, PlayerVo):
        	return obj.__dict__
        elif isinstance(obj, Decision):
        	return obj.__dict__
        else:
            return super(StateOfNatureEncoder, self).default(obj)


class Decision:
	INVEST  = "invest"
	GIVE 	= "give"
	ENSLAVE = "enslave"
	ATTACK 	= "attack"

	def __init__(self, type=None, playerName=None, amount=None):
		self.type = type
		self.playerName = playerName
		self.amount = amount

	def to_json(self):
		return json.dumps(self, cls=StateOfNatureEncoder)

	def from_json(self, jsondata):
		#data = json.loads(jsondata)
		data = jsondata
		self.type 		= data['type']
		self.playerName = data['playerName']
		self.amount 	= data['amount']


class PlayerVo:
	"""Represents a single player in the game."""
	 
	def __init__(self, id=None, name=None, numRounds=0, money=0):
		"""
		@param name
		@param numRounds the number of that will be played in this game (should probably be removed).
		@param money the amount of money the player has at the beginning of the game.
		"""
		self.id 		= id
		self.name 		= name
		self.decisions 	= [None] * numRounds
		self.money 		= money
		self.monies 	= [None] * (numRounds + 1)
		self.monies[0] 	= money
		self.master 	= None	

	def to_json(self):
		return json.dumps(self, cls=StateOfNatureEncoder)

	def from_json(self, jsondata):
		data = jsondata #json.loads(jsondata)
		self.id 		= data['id']
		self.name 		= data['name']
		self.money 		= int(data['money'])
		self.master 	= data['master']
		self.decisions 	= []
		self.monies 	= []
		for m in data['monies']:    		
			if m == None:
				self.monies.append(m)
			else:
				self.monies.append(int(m))	
		for d in data['decisions']:
			if d == None:
				self.decisions.append(d)
			else:
				decision = Decision()
				decision.from_json(d)
				self.decisions.append(decision)

	def get_decision(self, round):
		""" 
		The decision the player made in the given round.
	 	@param round from 0 to numRounds-1.
	 	"""
		return self.decisions[round]

	def has_money(self):		
		return self.money > 0
	
	def record_initial_money_for_round(self, round):
		"""
		At the end of a round, this method will be called and should 
		store the player's current money as the starting amount for this
		round in the players history.
		@param round the index of the round that is now starting, where index
		0 is the first round.  Note that this not really be called until the
		second round/index 1 because the first round/index 0 is set when the player
		is first created.
		"""
		self.monies[round] = self.money

	def is_enslaved(self):
		return self.master != None
	
	def is_decision_complete(self, round):
	    return self.is_enslaved() or (self.decisions[round] != None)
	
	def get_history(self):
		""" Returns a array of int representing the money the player had at the BEGINNING of each round."""
		return self.monies
   
	def invest(self, gameround):
		""" Invest current money at a 110 percent return. """
		self.decisions[gameround] = Decision(Decision.INVEST, None, -1);	
		self.money = round(self.money * 1.1)
	
	def give(self, gameround, amount, receiver):
		""" Give the specified amount of money to other player."""
		self.decisions[gameround] = Decision(Decision.GIVE, receiver.name, amount)
		self.money = (self.money - amount);
		receiver.money = (receiver.money + amount)
	
	def enslave_to(self, gameround, master):
		""" Sell self into slavery. """
		if (self.master != self):
			self.decisions[gameround] = Decision(Decision.ENSLAVE, master.name, -1)
			self.master = master
			self.master.money = (master.money + self.money)
			self.money = 0
	    	
	def attack(self, gameround, defender):
		""" Attack a player with less money and take up to 20.  IF the defender ends up with no moeny, they are eliminated."""
		self.decisions[gameround] = Decision(Decision.ATTACK, defender.name, -1)
		take = min(defender.money, 20)
		self.money = (self.money + take);
		defender.money = (defender.money - take);
	


class StateOfNatureVo:
	currentRound 	= 0
	maxRounds 		= 3
	players 		= []
	active_player 	= None

	def __init__(self, gameplayers=[]):
		i = 0
		
		self.players = [];
		for player in gameplayers:
			money = (i+1) * 10
			self.players.append(PlayerVo(player.user.id, player.nickname, self.maxRounds, money))
			i = i + 1
		self.maxRounds = 3
		self.currentRound = 0
		self._set_next_player()
	
	def to_json(self):
		""" Serialize game data to json string. """
		return json.dumps(self, cls=StateOfNatureEncoder)

	def from_json(self, jsondata):
		""" Load all the game data from a json string produced by to_json(). """
		#data = json.loads(jsondata)
		data = jsondata		
		self.currentRound 	= int(data['currentRound'])
		self.maxRounds 		= int(data['maxRounds'])
		self.active_player	= data['active_player']
		self.players 		= []
		for p in data['players']:
			if p == None:
				self.players.append(p)
			else:
				player = PlayerVo()
				player.from_json(p)
				self.players.append(player)

	#def get_player_names(self):
	#	return [player.name for player in self.players]
	def get_player_ids(self):
		return [player.id for player in self.players]

	def get_player_history(self, playerid):
		return self.get_player(playerid).get_history()

	def get_initial_money(self):
		self.get_monies()
		
	def get_monies(self):
		return [ player.money for player in self.players]
		
	def get_current_money(self, playerid):
		return self.get_player(playerid).money
	
	def get_current_decision(self, playerid):
		return self.get_player(playerid).get_decision(self.currentRound)		
	
	def get_player(self, playerid):
		try:
			return filter(lambda player: player.id == playerid, self.players)[0]
		except:
			return None

	def get_histories(self):
		histories = dict()
		for id in self.get_player_ids():
			histories[id] = self.get_player_history(id)
		return histories

	def is_game_completed(self):
		""" @return true if all the rounds are over or if there is only 1 player (with positive money) left. """
		# if all rounds over, game over
		if self.currentRound >= self.maxRounds:
			return True
		# if only 1 player has money, game over
		if self.num_players_with_money <= 1:
			return True
		return False
	
	def num_players_with_money(self):
		return sum (p.has_money() for p in self.players)		
	
	def invest(self, playerid):
		if self.get_player(playerid).is_enslaved():
			return
		self.get_player(playerid).invest(self.currentRound)
		self._goto_next_round_if_needed()
	
	def give(self, giver, amount, receiver):		
		if self.get_player(giver).is_enslaved() or self.get_player(receiver).is_enslaved():
			return
		if not self._can_give(giver, amount, receiver):
			return
		self.get_player(giver).give(self.currentRound, amount, self.get_player(receiver))
		self._goto_next_round_if_needed()

	def enslave(self, slavePlayer, masterPlayer):
		# what if master becomes enslaved??
		self.get_player(slavePlayer).enslaveTo(self.currentRound, self.get_player(masterPlayer))
		self._goto_next_round_if_needed()
			
	def attack(self, attacker, defender):
		if self.get_player(attacker).is_enslaved():
			return
		if not self._can_attack(attacker, defender):
			return
		self.get_player(attacker).attack(self.currentRound, self.get_player(defender))
		self._goto_next_round_if_needed()

	# -------------------
	# Private
	# -------------------

	def _goto_next_round_if_needed(self):
		gotoNextRound = False
		if self._is_round_completed():
			self._goto_next_round()
			gotoNextRound = True

		if self.is_game_completed():			
			return

		self._set_next_player()


	def _goto_next_round(self):
		self.currentRound = self.currentRound  + 1
		for pvo in self.players:
			pvo.record_initial_money_for_round(self.currentRound);		
	
	def _get_next_player(self):		
		minMoney = sys.maxint
		minPlayer= None		
		for p in self.players:			
			if (not (p.is_decision_complete(self.currentRound)) and (p.money < minMoney) and (not p.is_enslaved())):
				minPlayer = p;
				minMoney = p.money	
		return minPlayer;
	
	def _set_next_player(self):
		if self.is_game_completed():
			return
		p = self._get_next_player();
		if p != None:
			self.active_player = p.id

	def _is_round_completed(self):		
		for p in self.players:
			if (not p.is_decision_complete(self.currentRound)):
				return False			
		return True

	def _can_give(self, giver, amount, receiver):
		"""Make sure the giver not trying to give more than they have and that the receiver isn't dead."""
		if self.get_player(giver).money < amount:
			return False
		if self.get_player(receiver).money <= 0:  #because they're dead..
			return False
		return True

	def _can_attack(self, attacker, defender):
		return (self.get_player(attacker).money > self.get_player(defender).money)	







