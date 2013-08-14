/**
 *
 * @myid String is the id of the player who is playing.
 */
function StateOfNatureVo(jsonData, myid){	
	data = jsonData;


	this.currentRound 	= parseInt(data['currentRound']);
	this.maxRounds 		= parseInt(data['maxRounds']);
	this.players 		= [];
	this.active_player	= data['active_player']	

	for (i=0; i < (data['players']).length; i++){
		playerData = data['players'][i];
		p = new PlayerVo(playerData);
		this.players.push(p);
		if(p.id == myid){
			this.me = p;
		}
	}
	
	this.me = this.getPlayer(myid);
}


/**
 * Set the player who gets to make the next move.
 */
StateOfNatureVo.prototype.setNextPlayer = function(nextPlayerId){
	this.active_player = nextPlayerId;
}

/**
* Get the PlayerVo for the player with the given id.
* @return PlayerVo for player with given id.
*/
StateOfNatureVo.prototype.getPlayer = function(playerId){	
	for (var i = 0; i < this.players.length; i++){
		var p = this.players[i];		
		if(p.id == playerId){
			return p;
		}
	}
	return null;
}

/**
* Get the PlayerVo for the player with the given name.
* @return PlayerVo for player with given name.
*/
StateOfNatureVo.prototype.getPlayerNamed = function(playerName){	
	for (var i = 0; i < this.players.length; i++){
		var p = this.players[i];		
		if(p.name == playerName){
			return p;
		}
	}
	return null;
}

StateOfNatureVo.prototype.getCurrentPlayerIndex = function(){
	for (var i = 0; i < this.players.length; i++){
		var p = this.players[i];		
		if(p.id == this.active_player){
			return i;
		}
	}
	return -1;
}

/**
 * Return the player with the most money (can be used to get the winner at the end of the game).
 */
StateOfNatureVo.prototype.getRichestPlayer = function(){	
	var richestPlayer = this.players[0];
	for (var i = 0; i < this.players.length; i++){		
		var p = this.players[i];		
		if(p.money > richestPlayer.money){
			richestPlayer = p;		
		}
	}
	return richestPlayer;
}