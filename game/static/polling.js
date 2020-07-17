let currentState = null,
  pollingInterval;
let currentRound = null;
let guessName = null;
let passName = null;
let currentRoom = null;
let initialised = null;

function play() {
  $(".playbtn").hide();
  let game = document.getElementById("game");
  game.classList.remove("invisible");
  // Start Timer
  $.get("/startTimer", function (response) {
    console.log(response);
  });
}

function scorePoint() {
  $.get("/point/" + guessName[0] +"/"+ currentRound, function (response) {
    console.log(response);
    setGuessName();
  });
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function whosPlaying(response) {
  let npInfo = document.getElementById("not_playing_info");
  npInfo.innerHTML = "";
  let para = document.createElement("h1");
  para.className = "text-center text-white";
  let name = "It's " + response.currentPlayer[1] + "'s turn to play";
  para.append(name);
  let timer2 = response.Time;
  let br = document.createElement("br");
  para.append(br);
  para.append(timer2);

  npInfo.appendChild(para);
}

function setTimer(response) {
  let timer1 = document.getElementById("playing_timer");
  timer1.innerHTML = response.Time;
}

function initialise(playing) {
  if (initialised == true) {
    return;
  }
  if (playing == "in_play") {
    initialised = true;
    let play_areacls = document.getElementById("play_area");
    play_areacls.classList.remove("invisible");
    $(".staging_timer").hide();
    $(".play_area").show();
    $(".playbtn").show();
    console.log("initialise Complete");
  } else {
    initialised = true;
    let notplaying_timer = document.getElementById("notplaying_timer");
    notplaying_timer.classList.remove("invisible");
    $(".play_area").hide();
    $(".staging_timer").show();
  }
  $(".scorecard").hide();
}

function reset() {
  initialised = false;
  let play_area = document.getElementById("play_area");
  let notplaying_timer = document.getElementById("notplaying_timer");
  let game = document.getElementById("game");
  game.classList.add("invisible");
  notplaying_timer.classList.add("invisible");
  play_area.classList.add("invisible");
  console.log("Reset Complete");
}

function createScores(top_team, bottom_team, score) {
  if (currentRound == "rnd1") {
    round = "End of Round One";
  } else if (currentRound == "rnd2") {
    round = "End of Round Two";
  } else if (currentRound == "rnd3") {
    round = "End of Round Three";
  }
  let inner = document.getElementById("scorecard_inner");
  inner.innerHTML = "";
  let div = document.createElement("div");
  div.className = "card bg-light mb-3";
  div.style = "max-width: 18rem;";
  let div2 = document.createElement("div");
  div2.className = "card-body";
  div.append(div2);
  let h5title = document.createElement("h5");
  div2.append(h5title);
  let title = round + " Scores";
  h5title.append(title);
  let topp = document.createElement("p");
  
  let bottp = document.createElement("p");
  div2.append(bottp);
  let topscore = top_team + ": " + score[0];
  topp.append(topscore);
  div2.append(topp);
  let bottscore = bottom_team + ": " + score[1];
  bottp.append(bottscore);
  inner.append(div);
}

function scorecard(scores) {
  $(".play_area").hide();
  $(".staging_timer").hide();
  $(".scorecard").show();
  if (scores[0] > scores[1]) {
    createScores("Green Team", "Red Team", scores);
  } else {
    createScores("Red Team", "Green Team", scores);
  }
}

function namesLeft(number) {
  let namesleft = document.getElementById("namesleft");
  namesleft.innerHTML = "Names Left: " + String(number);
}

function setGuessName() {
  $.get("/getNewName/" + currentRound, function (response) {
    console.log(response);
    let guess = document.getElementById("guessnamehere");
    let added = document.getElementById("addedbyhere");
    if (response.newRound == true) {
      guess.innerHTML = null;
      added.innerHTML = null;
    } else {
      guessName = response.namesToGuess[0];
      guess.innerHTML = guessName[1];
      added.innerHTML = "added by " + guessName[2];
    }
  });
}

function gameOver(roomCode) {
  window.location.replace('/gameOver/'+roomCode);
}

let isPlaying = $("#playbutton").length;
if (isPlaying > 0) {
  let playbutton = document.getElementById("playbutton");
  playbutton.classList.remove("invisible");
}

jQuery(document).ready(function ($) {
  pollingInterval = setInterval(function () {
    intervalPoll();
  }, 1000);

  function intervalPoll() {
    $.get("/response", function (response) {
      console.log(response);

      currentRoom = response.roomCode;
      currentRound = response.rndNo;

      if (response.rndNo == "End") {
        gameOver(currentRoom);
        return;
      }

      if (response.scorecard == true) {
        scorecard(response.scores);
        return;
      }

      if (response.currentPlayer[0] != getCookie("user_id")) {
        initialise("not_in_play");
        whosPlaying(response);
      } else {
        initialise("in_play");
        if (guessName == null) {
          setGuessName();
        }
      }

      if (response.timerStarted == true) {
        setTimer(response);
      }      

      if (response.newPlayer == true) {
        reset();
      }

      let isPlaying = $("#guessnamehere").length;
      if (isPlaying <= 0) {
        return;
      }
      
    });
  }
});

// TODO:

// Create Screen to explain round
// Create Play Again Screen

// BUGS:
// Refreshing gets a new name
