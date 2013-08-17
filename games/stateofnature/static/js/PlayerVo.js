function PlayerVo(data){
    this.id 		= data['id'];
    this.name 		= data['name'];
    this.money 		= data['money'];
	this.master 	= data['master'];
	
	this.monies 	= new Array();
	for (var i=0; i < data.monies.length; i++){
		var m =  data['monies'][i];
		if ( m == 'null'){
			this.monies[i] = null;
		}else{
			this.monies[i] = parseInt(m);
		}
	}	

	this.decisions 	= new Array();
	for (var i=0; i < data['decisions'].length; i++){
		var d = data['decisions'][i];
		if ( d == null){
			this.decisions[i] = null;
		}else{
			this.decisions[i] = d['type'];
		}
	}  
	//this.active = false;
}

PlayerVo.prototype = {
	id: null,
	name: null,
	money: null,	
	master: null,
	decisions: null,
	monies: null,
	
	//active: null,
	getMoneyForRound: function (round){
	    return this.monies[round];
	},
	getDecisionForRound: function (round){
	    return this.decisions[round];
	},
	isEnslaved: function (){
		return (this.enslavedTo != null);
	},
}
