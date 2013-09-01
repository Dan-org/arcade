from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
import jsonfield
import json
import sys



class Game(models.Model):
	""" Game represents a type of game that can be downloaded via a repository and played on the loft. """
	name 		= models.CharField(max_length=20)
	dir 		= models.SlugField()	
	#repository 	= models.URLField(max_length=200)
	repository 	= models.CharField(max_length=200)
	
	min_players = models.IntegerField(default=1)		# let instructor set this so we can switch between testing / production / and different classes?
	max_players = models.IntegerField(default=10)

	class Meta:
		ordering = ("name",)

	def __unicode__(self):
		return self.name


class Player(models.Model):
	"""
	Associates a user with a nickname to avoid custom user model issues.
	"""
	user 		= models.ForeignKey(settings.AUTH_USER_MODEL)
	nickname 	= models.CharField(max_length=24)

	class Meta:
		ordering = ("nickname",)

	def __unicode__(self):
		return self.nickname


ROOM_STATES = (
    ('getting-ready', 	"getting ready"), 	# Players are joining game, but hasn't started yet
    ('in-progress', 	"in progress"),     # Game has started
    ('over', 			"over"),       		# Game is over
)

class Room(models.Model):
	""" Room represents a group of players that want to play a particular type of game """	
	game 	= models.ForeignKey(Game, related_name="rooms")
	name 	= models.CharField(max_length=24)
	players = models.ManyToManyField(Player, blank=True, null=True, related_name="rooms_joined")	
	json	= jsonfield.JSONField()	
	status 	= models.SlugField(choices=ROOM_STATES, default='getting-ready') # -- be nice and set this so arcade can clean up game and display stuatus	

	#is_joinable = models.BooleanField(default=True) -- this is actually a property of the status, player and gametime, so  can't really set it here
	#can_watch 
	

	class Meta:
		ordering = ("name",)

	def __unicode__(self):
		return self.name

	#@models.permalink
	#def get_absolute_url(self):
	#	return ("room", (self.slug,))
	
