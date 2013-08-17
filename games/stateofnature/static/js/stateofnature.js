  /*
    These variables must be set for this script to work

    ROOM_ID="{{ game.room.id }}";
    GAME_ID="{{ game.id }}";
    USER_NAME="{{ user.username }}";
  */

  //var stateOfNatureVo;
  var STATE_OF_NATURE;
  var ROOM_ID;
  //var userName;
  //var roomId;
  var zoneId;
  var checkConnection; 
  var roomlist;
  var gameList;
  var users;


  //interface constants
  var rowHeight = 20;
  var canvas_width = 600;
  var canvas_height = 350;

  var NULL_PLAYER_OPTION = "[choose player]";

 
  
  // will execute init when the window loads
  addLoadEvent( function(){   
    
    // ADD ROOM BUTTONS    
    $('#create_room_button').click(function (event){
        var roomname = $("#create_room_name").val();              
        $('#create_room_name').val('');
        politicssocket.emit('create_room', roomname);
    });

    // START GAME BUTTON
    $('#start_game_button').click(function (event){
      //alert("boo " + ROOM_NAME + " " + USER_NAME)
      politicssocket.emit('create_game');
    });

    // GAMEBOARD ACTION BUTTONS
    $('#investButton').click(function (event) {
        invest();
    });
    $('#attackButton').click(function (event) {
        var victimName = $('#attackPlayer').val();  
        attack(victimName);
    });
    $('#enslaveToButton').click(function (event) {
        var masterName = $('#enslaveToPlayer').val(); 
        enslaveTo(masterName);
    });
    $('#giveToButton').click(function (event) {
        var beneficiaryName = $('#giveToPlayer').val();
        var amount = $('#giveToAmount').val();
        giveTo(beneficiaryName, amount);
    });

    //disable button unless player chosen
    //checkAttackPlayer();
    $("#attackPlayer").change(checkAttackPlayer);
    $("#enslaveToPlayer").change(checkEnslavePlayer);
    $("#giveToPlayer").change(checkGiveToPlayer);

    //show/hide info
    $("#goals-link").click(function(event){ showinfo("goals"); });
    $("#rules-link").click(function(event){ showinfo("rules"); });
    $("#game-link").click(function(event){ showinfo("game"); });
    
    gotopage('rooms');
    //gotopage('game');
    //gotopage('end');
  });


  var politicssocket = io.connect("/playpolitics");

  politicssocket.on('connect',      function () { politicssocket.emit('enter_zone'); });
  politicssocket.on('reconnect',    function () {});
  politicssocket.on('reconnecting', function () {});
  politicssocket.on('error',        function (e) {});
  politicssocket.on('enter_zone',   function (rooms) { show_rooms(rooms); });
  politicssocket.on('room_created', function (rooms) { show_rooms(rooms); });
  
  politicssocket.on('joined_room',  function(){ 
    gotopage('lobby') });

  politicssocket.on('join_me', function(){  
    politicssocket.emit('join_game'); });

  politicssocket.on('begin_game', function (stateofnature) {  
    gotopage("game");
    update(stateofnature);
  });

  politicssocket.on('next_player', function (next_player) {
    STATE_OF_NATURE.setNextPlayer(next_player);
    updateGame(STATE_OF_NATURE);
  });

  politicssocket.on('next_round', function (stateofnature) { update(stateofnature); });
  politicssocket.on('invest',     function (stateofnature) { update(stateofnature); });
  politicssocket.on('attack',     function (stateofnature) { update(stateofnature); });
  politicssocket.on('give',       function (stateofnature) { update(stateofnature); });
  politicssocket.on('enslave',    function (stateofnature) { update(stateofnature); });

  politicssocket.on('end_game',     function (stateofnature) {
    gotopage('end');
    update(stateofnature);
    showWinner(STATE_OF_NATURE);
  });


  //======================
  // USER INPUT
  //=======================


  function invest(){ 
    // tell server this player is investing
    politicssocket.emit('invest', STATE_OF_NATURE.me.id);
    endTurn();
  }

  function attack(victimName){
    // tell the server this player is attacking another player
    var me = STATE_OF_NATURE.me;
    var victim = STATE_OF_NATURE.getPlayerNamed(victimName);
    if (victim.money >= me.money) {
      alert("Can't attack a player with more money than you.");
      return;
    }
    politicssocket.emit('attack', me.id, victim.id);
    endTurn();
 }

 function giveTo(recipientName, amount)
 {
    var me = STATE_OF_NATURE.me;
    var recipient = STATE_OF_NATURE.getPlayerNamed(recipientName);

    if (!isNaN(amount) && recipient !== undefined) {
      if (amount < 0 || amount > me.money) {
        // TODO: something better than an alert box
        alert("You don't have enough to give " + recipient.name + " $" + amount + "!");
        return;
      }
      politicssocket.emit('give', me.id, recipient.id, amount);
    } else {
      // signal error
    }
    endTurn();
  }

  // tell the server this player is enslaving themself to another player
  function enslaveTo(masterName){    
    var me = STATE_OF_NATURE.me;
    var master = STATE_OF_NATURE.getPlayerNamed(masterName);       
    if (!master.isEnslaved()) {
      politicssocket.emit('enslave', me.id, master.id);
      //this should be done after message received....???
      //getPlayerInfo(me).enslavedto = opInfo;
      endTurn(); 
      } 
    else {
      alert("You can't enslave yourself to another slave!");
      }
  }


//======================
// Manipulate dom
//=======================


  
  //----------------
  // Rooms
  //----------------

  function show_rooms(rooms){
    room_html = '';

    // Create a list of rooms
    if(rooms.length > 0){
      for (var i = 0; i < rooms.length; i++){
        room = rooms[i];      
        player_html = '';
        for(var j = 0; j < room['players'].length; j++){
          player = room['players'][j];
          player_html = player_html + ' ' + player;
          
        }          
        room_html = room_html + 
          '<tr>' +
          '<td width="100px">' + room['name'] + '</td>' + 
          '<td width="100%">' + player_html + '</td>' +
          '<td width="100px">' + '<input type="submit" class="room_link" id="'+ room['id'] +'" value="Join">' + '</td>' +
          '</tr>';
      }
      $('#room_list').html('<table>' + room_html + '</table>');
    }
    // add a link to each of the rooms that sends a message to socket to join room
    $('.room_link').each(function() {
        $(this).click(function(event){                     
          ROOM_ID = $(this).attr("id");
          politicssocket.emit('join_room', ROOM_ID, USER_ID, NICKNAME);
          join_room(ROOM_ID, NICKNAME);
        });
    });
  }



  //----------------
  // Game
  //----------------
  
  function update (stateofnature){
    var son = JSON.parse(stateofnature);
    STATE_OF_NATURE = new StateOfNatureVo(son, USER_ID);
    updateGame(STATE_OF_NATURE);    
  }

  function gotopage(page){
    if(page == "rooms"){
      $('#rooms').show();
      $('.lobby').hide();
      $('#chat').hide();
      $('#gameboard').hide();
      $('#nature-actions').hide();
      showinfo("nothing");
      $('#gameover').hide();

    }else if(page == "lobby"){
      $('#rooms').hide();
      $('.lobby').show();
      $('#chat').show();
      $('#gameboard').hide();
      $('#nature-actions').hide();
      showinfo("nothing");
      $('#gameover').hide();

    }else if(page == "game"){
      $('#rooms').hide();
      $('.lobby').hide();
      $('#chat').show();
      $('#gameboard').show();
      $('#nature-actions').show();
      showinfo("info");
      $('#gameover').hide();

      //remove extra players

    }else if(page == "end"){
      $('#rooms').hide();
      $('.lobby').hide();
      $('#chat').show();
      $('#gameboard').show();
      $('#nature-actions').hide();
      showinfo("nothing");
      $('#gameover').show();
      
    }
  }

  function showinfo(page){
    $('#goals').hide(); 
    $('#rules').hide(); 
    $('#game').hide(); 

    if(page == "nothing"){
      $('#info').hide();
    }else{
      $('#info').show();
    }

    if(page == "rules"){      
      $('#rules').show();       
    }else if(page == "goals"){
      $('#goals').show();
    }else if(page == "game"){
      $('#game').show();
    }

  }

  /**
   * Update the scoreboard and player options.
   * @param stateOfNatureVo that holds all a copy of all the game state info.
   */
  function updateGame(stateOfNatureVo){
    updateScoreboard(stateOfNatureVo);
    highlight(stateOfNatureVo.getCurrentPlayerIndex(), stateOfNatureVo.currentRound);    
    updateActionButtons(stateOfNatureVo);
  }

  /**
   * Called after the player chooses an action in order to disable the interface immediately
   * until the action can be sent to the server.
   */
  function endTurn(){
      //highlightPlayer(-1);  // unhighlight all the players
    disableActionButtons(); //disable buttons
  }

  /*
   * Gets all the money values for each player out of the stateofNatuerVo and puts in the table view.
   */
  function updateScoreboard(stateOfNatureVo){  
      //remove extra rows of table
      var numplayers = stateOfNatureVo.players.length + 1;
      $('#nature-table tr:gt(' +numplayers+ ')').remove();

      for (var i=0; i < stateOfNatureVo.players.length; i++) {        
        var player = stateOfNatureVo.players[i];

        // draw player names in the scoreboard        
        $('#nature-table > tbody > tr:eq('+i+') td.player').text(player.name);

        for(var j=0; j < stateOfNatureVo.maxRounds; j++){
          var money;
          var decision;

          if(stateOfNatureVo.currentRound >= j){
            //if we are showing the current round, use the value in monies
            if(j == stateOfNatureVo.currentRound){
              money = player.money;              
            }else{
              //if we are in a previous round, use the money saved at start of _next_ round, that
              // is because monies saves the value at the start of the round, but we want to display the
              // end of the round
              money = player.monies[j+1];                
            }
            decision = player.decisions[j];            
          }else{
            money = "";
            decision = "";
          }
          if (decision == null){
            decision = ""
          }
          $('#nature-table > tbody > tr:eq('+i+') td.money.round'+j).text(money);
          $('#nature-table > tbody > tr:eq('+i+') td.decision.round'+j).text(decision);
        }
      }
  }

  /**
   * Sets the header columns of the round highlighted or not as well as the money and decisions.
   */
  function highlight(currentPlayerIndex, currentRoundIndex){
    
    //hightlight header of current rounds    
    $('#nature-table th').removeClass('highlight');
    var i = currentRoundIndex;
    if(i >= 0){
      $('#nature-table th.round' + i).addClass('highlight');
    }
    // highlight player decision and money
    // start by unhighlighting all
    $('#nature-table td').removeClass('highlight');
    $('#nature-table td').removeClass('player-highlight');    
    // highlight correct row
    var p = currentPlayerIndex;
    if (p >= 0){
      $('#nature-table > tbody > tr:eq('+p+') td.round'+i).addClass('highlight');    
      $('#nature-table > tbody > tr:eq('+p+') td.player').addClass('player-highlight');
      $('#nature-table > tbody > tr:eq('+p+') td.arrow').addClass('highlight');
    }
  }

  /**
   * Disable action buttons if not the players turn, otherwise setup the buttons appropriately.
   */
  function updateActionButtons(stateOfNatureVo){
    var playerVos             = stateOfNatureVo.players;
    var me                    = stateOfNatureVo.me;
    var currentRoundIndex     = stateOfNatureVo.currentRound;
    var attackablePlayerNames = new Array();
    var notMePlayerNames      = new Array();  
    
    if((me.id == stateOfNatureVo.active_player)) // && !me.isEnslaved())  shouldn't need ot check for this...
    {
      $('#investButton').removeAttr("disabled");
      $('#attackPlayer').removeAttr("disabled");
      $('#enslaveToPlayer').removeAttr("disabled");
      $('#giveToPlayer').removeAttr("disabled");
      $('#giveToAmount').removeAttr("disabled");
      //$('#giveToAmount').attr("enabled", true); //have to do this because of jstepper??
    
      //setup player names
      for (var i=0; i < playerVos.length; i++) {
        var p = playerVos[i];
        console.log("p ", p);
        if ( p.name != me.name){        
          notMePlayerNames.push(p.name);
          if(me.money > p.money){
            attackablePlayerNames.push(p.name);
          }
        }
      }   
      setOptions($('#attackPlayer'),    createPlayerOptionsHtml(attackablePlayerNames));
      setOptions($('#enslaveToPlayer'), createPlayerOptionsHtml(notMePlayerNames));
      setOptions($('#giveToPlayer'),    createPlayerOptionsHtml(notMePlayerNames));
      
      //restrict numerical stepper  
      //$('#giveToAmount').jStepper({minValue:0, maxValue:me.money}); 
      //$('#giveToAmount').textinput('refresh');
        
      checkAttackPlayer();
      checkEnslavePlayer();
      checkGiveToPlayer();
    }else{
      disableActionButtons();
    }
  }

  /**
   * Disable all the players buttons for taking actions.
   */
  function disableActionButtons()
  {
    $('#investButton').attr('disabled', 'disabled');
    $('#attackButton').attr('disabled', 'disabled');
    $('#attackPlayer').attr('disabled', 'disabled');
    $('#enslaveToButton').attr('disabled', 'disabled');
    $('#enslaveToPlayer').attr('disabled', 'disabled');
    $('#giveToButton').attr('disabled', 'disabled');
    $('#giveToPlayer').attr('disabled', 'disabled');
    $('#giveToAmount').attr('disabled', 'disabled');

    //attached jquery.jstepper to this so need to use 
    //$('#giveToAmount').attr("disabled", true); //have to do this because of jstepper??
  }

  /**
   * Create the options for a drop-down list with all the players names.
   */
  function createPlayerOptionsHtml(playerNameArray){    
    var playerHtml = '<option data-placeholder="true">' + NULL_PLAYER_OPTION + '</option>';
    var i;
    for (i = 0; i < playerNameArray.length; i++) {
        playerHtml += '<option>' + playerNameArray[i] + '</option>';
    }
    return playerHtml;
  }

  /**
   * Helper function to set the values of a select widget.
   */ 
  function setOptions(select, optsHtml){
    select.empty();
    select.html(optsHtml);
    //select.selectmenu('refresh');
  }
        
  /**
   * Disables the action button if no player selcted in the drop-down list.
   */
  function checkAttackPlayer() { enableAction($("#attackButton"),    $('#attackPlayer'));  }
  function checkEnslavePlayer(){ enableAction($("#enslaveToButton"), $('#enslaveToPlayer')); }
  function checkGiveToPlayer() { enableAction($("#giveToButton"),    $('#giveToPlayer'));    }

  /**
   * Checks the player drop-down list and disables/enables the given button if a player is selected.
   */
  function enableAction(actionButton, playerSelect){
    var selectedVal = playerSelect.val() ;
    var isPlayerSelected = (selectedVal != NULL_PLAYER_OPTION) && (selectedVal != null);
    if(isPlayerSelected){
        //actionButton.button('enable');
        actionButton.removeAttr("disabled");
    }else{
        //actionButton.button('disable');
        actionButton.attr('disabled', 'disabled');
    } 
  }


//--------------------------
// Post mortem 
//--------------------------

/**
 * Update the scoreboard and player options.
 * @param stateOfNatureVo that holds all a copy of all the game state info.
 */
function showWinner(stateOfNatureVo){
  highlight(-1, -1)  
  var name = stateOfNatureVo.getRichestPlayer().name;
  
  $('.winner').text(name);  
  flashWinner();
}

//relies on jquery.pulse.js
function flashWinner(){
  var properties = { opacity: 0.25 };
  var el = $('#win-text');
  el.pulse(properties, {
    duration : 1000,
    pulses   : 7,
    interval : 100
    });
}


