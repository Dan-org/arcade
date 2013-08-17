from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from subprocess import call

from arcade.models import Game

@staff_member_required
def fetchgame(request, game_id):
	#room = get_object_or_404(Room, slug=slug)    
    print "game id %s" % game_id

    game = Game.objects.get(pk=game_id)
    print game.repository
    return redirect('/admin/arcade/game/%s' % game_id)
	#retcode = call(["/full/path/myscript.py", "arg1"])