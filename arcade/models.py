from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
import jsonfield
import json
import sys



class Game(models.Model):
	""" Game represents a type of game that can be downloaded via a repository and played on the loft. """
	name 		= models.CharField(max_length=20)
	repository 	= models.URLField(max_length=200)

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

class Room(models.Model):
	""" Room represents a group of players that want to play a particular type of game """
	game 	= models.ForeignKey(Game, related_name="rooms")
	name 	= models.CharField(max_length=24)
	players = models.ManyToManyField(Player, blank=True, null=True, related_name="rooms_joined")
	is_open = models.BooleanField(default=True)

	class Meta:
		ordering = ("name",)

	def __unicode__(self):
		return self.name

	#@models.permalink
	#def get_absolute_url(self):
	#	return ("room", (self.slug,))
