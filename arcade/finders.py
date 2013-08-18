from collections import OrderedDict
from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles.storage import FileSystemStorage
from django.conf import settings
from django.utils._os import upath
from importlib import import_module

import os


class ArcadeStaticStorage(FileSystemStorage):
	"""
	A file system storage backend that takes an game directory and works
	for the ``static`` directory of it.
	"""
	prefix = None
	source_dir = 'static'

	def __init__(self, game, *args, **kwargs):		
		"""
		Returns a static file storage if available in the given game dir.
		"""
		# app is the actual app module
		mod = import_module(game)
		mod_path = os.path.dirname(upath(mod.__file__))		
		location = os.path.join(mod_path, self.source_dir)		
		super(ArcadeStaticStorage, self).__init__(location, *args, **kwargs)



class ArcadeDirectoriesFinder(BaseFinder):
	"""
	A static files finder that looks in the directory of each app as
	specified in the source_dir attribute of the given storage class.
	"""
	storage_class = ArcadeStaticStorage

	def __init__(self, games=None, *args, **kwargs):
		# The list of apps that are handled
		self.games = []
		# Mapping of app module paths to storage instances
		self.storages = OrderedDict()

		#if games is None:
		#    games = settings.INSTALLED_APPS
		if games is None:
			arcade_base_dir = os.path.basename(settings.ARCADE_PATH)
			games = os.walk("%s" % settings.ARCADE_PATH).next()[1]  #all the subdirs of ARCADE_DIR
			games = [ arcade_base_dir + "."  + game  for game in games]

		for game in games:
			game_storage = self.storage_class(game)
			if os.path.isdir(game_storage.location):
				self.storages[game] = game_storage
				if game not in self.games:
					self.games.append(game)
		super(ArcadeDirectoriesFinder, self).__init__(*args, **kwargs)


	def list(self, ignore_patterns):
		"""
		List all files in all app storages.
		"""
		for storage in six.itervalues(self.storages):
			if storage.exists(''): # check if storage location exists
				for path in utils.get_files(storage, ignore_patterns):
					yield path, storage

	def find(self, path, all=False):
		"""
		Looks for files in the app directories.
		"""
		matches = []
		for game in self.games:
			match = self.find_in_game(game, path)
			if match:
				if not all:
					return match
				matches.append(match)
		return matches

	def find_in_game(self, game, path):
		"""
		Find a requested static file in an app's static locations.
		"""
		storage = self.storages.get(game, None)
		if storage:
			if storage.prefix:
				prefix = '%s%s' % (storage.prefix, os.sep)
				if not path.startswith(prefix):
					return None
				path = path[len(prefix):]
			# only try to find a file if the source dir actually exists
			if storage.exists(path):
				matched_path = storage.path(path)
				if matched_path:
					return matched_path

