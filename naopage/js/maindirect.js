
var session = null;
var debug = true;
var session = null;
var animatedSay = null;
var behaviourManager = null;
var motion = null;
var posture = null;
var video = null;
var system =null;
var life =null;
var tablet = null;
var navigation =null;
var speed = 0.1;

QiSession(function (Qisession) {
    session = Qisession;
    console.log("connected!");
    // you can now use your QiSession
    session.service("ALBehaviorManager").then(StartBehaviourService, nao.error);
    session.service("ALAnimatedSpeech").then(StartAnimatedSpeechService, nao.error);
    session.service("ALSystem").then(StartSystem, nao.error);
    session.service("ALMotion").then(StartMotionSystem, nao.error);
    session.service("ALNavigation").then(StartNavigationSystem, nao.error);
    session.service("ALVideoDevice").then(StartVideoSystem, nao.error);
    session.service("ALRobotPosture").then(StartPostureSystem, nao.error);
    session.service("ALAutonomousLife").then(StartLifeSystem, nao.error);
    session.service("ALTabletService").then(StartTabletSystem, nao.error);

}, function () {
    console.log("disconnected");
});


function StartSystem(system) {
    nao.system = system;
    nao.log("System Started")
}
function StartMotionSystem (motion) {
    nao.motion = motion;
    nao.log("Motion ok");
}
function StartNavigationSystem (navigation) {
    nao.navigation = navigation;
    nao.log("Navigation ok");
}
function StartPostureSystem (posture) {
    nao.posture = posture;
    nao.log("Posture ok");
}
function StartVideoSystem (video) {
    nao.video = video;
    nao.log("Video ok");
}
function StartBehaviourService (bm) {
    nao.behaviourManager = bm;
    nao.log("Behaviour ok");
}
function StartAnimatedSpeechService (tts) {
    nao.animatedSay = tts;
    nao.log("Animated Speech ok")
}
function StartLifeSystem (life) {
    nao.life = life;
    nao.log("Auto Life ok")
}
function StartTabletSystem (tablet) {
    nao.tablet = tablet;
    nao.log("tablet Started")
}




function selectBehaviour() {
    document.getElementById("myDropdown").classList.toggle("show");
    getBehaviours();
}

function filterFunction() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    div = document.getElementById("myDropdown");
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
        txtValue = a[i].textContent || a[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            a[i].style.display = "";
        } else {
            a[i].style.display = "none";
        }
    }
}

var randomCall
function startRandomBehaviour(){
    getBehaviours();
    console.log("random start");
    randomCall = setInterval(callRandomBehaviour, 30000);

}
function stopRandomBehaviour(){
    console.log("random stop");
    clearInterval(randomCall);
}

function callRandomBehaviour(){
    nao.behaviourManager.getInstalledBehaviors().then(function (data) 
    {
        var b = getRandomInt(data.length - 1);
        console.log(data[b]);
        behaviourManager.runBehavior(data[b]);

    });

}

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

function getBehaviours() {
    console.log("getBehaviours")
    behaviourManager.getInstalledBehaviors().then(function (data) {
        for (let i = 0; i < data.length; i++) {
            $('#myDropdown').append("<a class='behaviourLink'>" + data[i] + "</a>");
            
            if (data[i].startsWith("animations/Stand/Gestures/")) {
                $('#gestures').append("<button class='behaviourLink'>" + data[i] + "</button>");
            }
            if (data[i].startsWith("animations/Stand/Reactions/")) {
                $('#reactions').append("<button class='behaviourLink'>" + data[i] + "</button>");
            }
            if (data[i].startsWith("animations/Stand/Waiting/")) {
                $('#waiting').append("<button class='behaviourLink'>" + data[i] + "</button>");
            }
        }
        $('.behaviourLink').click(function () {
            console.log($(this)[0])
            console.log($(this)[0].innerText)
            behaviourManager.runBehavior($(this)[0].innerText);
        })

    })
}

function runBehaviour(behaviour) {
    behaviourManager.runBehavior(behaviour);
}

function stopAll() {
    behaviourManager.stopAllBehaviors();
}

function randomHello() {

    var rnd = Math.floor(Math.random() * 4);

    switch (rnd) {
        case 0:
            animatedSay.say("Hello!");
            break;
        case 1:
            animatedSay.say("Hi!");
            break;
        case 2:
            animatedSay.say("Hi There!");
            break;
        case 3:
            animatedSay.say("Nice to see you!");
            break;
        default:
            animatedSay.say("Hello!");
            break;
    }
}

function displayImage(image) {
    tablet.showImage(image);
}