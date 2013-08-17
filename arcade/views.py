import os
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from subprocess import call
from arcade.models import Game


@staff_member_required
def fetchgame(request, game_id):
	game = Game.objects.get(pk=game_id)

	# check game not null
	if settings.ARCADE_DIR == None:
		pass

	#print game.dir
	#print game.repository
	# check arcade dir exists

	_do_fetchgame(settings.ARCADE_DIR, game.dir, game.repository)


	#retcode = call(["/full/path/myscript.py", "arg1"])
	return redirect('/admin/arcade/game/%s' % game_id)
	



def _do_fetchgame(arcade_dir_path, game_dir, repository):
	# look in arcade dir for game
	exists = os.path.exists(os.path.join(arcade_dir_path, game_dir))

	if not exists:		
		cmds = ["git", "clone", repository, "%s%s" % (arcade_dir_path, game_dir)]
		retcode = call(cmds)	
	else:
		# get fetch origin
		path = "%s%s/.git" % (arcade_dir_path, game_dir)
		#cmds = ["git", "--git-dir", path, "fetch", "origin"]
		
		cmds = ["git", "--git-dir", path, "fetch", "--tags"]
		retcode = call(cmds)

		cmds = ["git", "--git-dir", path, "checkout", "master"]
		retcode = call(cmds)
		
		cmds = ["git", "--git-dir", path, "pull", "origin", "master"]
		retcode = call(cmds)
		
