var nao = {
    debug: true,
    session: null,
    animatedSay: null,
    behaviourManager: null,
    motion: null,
    posture: null,
    video: null,
    system: null,
    life: null,
    tablet:null,
    navigation: null,
    speed: 0.1,


    init: function (address) {
        console.log("Nao Control loading");

        QiSession(function (Qisession) {
            nao.session = Qisession;
            console.log("connected!");
            // you can now use your QiSession
            nao.session.service("ALBehaviorManager").then(nao.StartBehaviourService, nao.error);
            nao.session.service("ALAnimatedSpeech").then(nao.StartAnimatedSpeechService, nao.error);
            nao.session.service("ALSystem").then(nao.StartSystem, nao.error);
            nao.session.service("ALMotion").then(nao.StartMotionSystem, nao.error);
            nao.session.service("ALNavigation").then(nao.StartNavigationSystem, nao.error);
            nao.session.service("ALVideoDevice").then(nao.StartVideoSystem, nao.error);
            nao.session.service("ALRobotPosture").then(nao.StartPostureSystem, nao.error);
            nao.session.service("ALAutonomousLife").then(nao.StartLifeSystem, nao.error);
            nao.session.service("ALTabletService").then(nao.StartTabletSystem, nao.error);

        }, function () {
            console.log("disconnected");
        }, address);

    },
    error: function (error) {
        console.log("An error occurred:", error)
    },


    StartSystem: function (system) {
        nao.system = system;
        nao.log("System Started")
    },
    StartMotionSystem: function (motion) {
        nao.motion = motion;
        nao.log("Motion ok");
    },
    StartNavigationSystem: function (navigation) {
        nao.navigation = navigation;
        nao.log("Navigation ok");
    },
    StartPostureSystem: function (posture) {
        nao.posture = posture;
        nao.log("Posture ok");
    },
    StartVideoSystem: function (video) {
        nao.video = video;
        nao.log("Video ok");
    },
    StartBehaviourService: function (bm) {
        nao.behaviourManager = bm;
        nao.log("Behaviour ok");
    },
    StartAnimatedSpeechService: function (tts) {
        nao.animatedSay = tts;
        nao.log("Animated Speech ok")
    },
    StartLifeSystem: function (life) {
        nao.life = life;
        nao.log("Auto Life ok")
    },
    StartTabletSystem: function (tablet) {
        nao.tablet = tablet;
        nao.log("tablet Started")
    },
    log: function (output) {
        if (nao.debug) {
            console.log(output)
        }
    },

    spin360: function () {
        nao.motion.move(0.0, 0.0, Math.PI * 2);
    },
    spin180: function () {
        nao.motion.move(0.0, 0.0, Math.PI);
    },
    spinHandsup: function (tosay) {
        nao.behaviourManager.runBehavior("dialog_move_arms/animations/UpBothArms")
        nao.motion.move(0.0, 0.0, Math.PI * 2);
        nao.animatedSay.say(tosay);
    },
    explore: function (radius) {
        if (!radius) {
            radius = 10;
        }
        nao.navigation.explore(radius);
    },
    stopExplore: function () {

        nao.navigation.stopExploration()
    },
    moveTo : function (vdirection,localSpeed){
        if (!localSpeed) {
            localSpeed = speed;
        }


        if (!vdirection) {
            vdirection = "forward";
        }

        vspeed = parseFloat(localSpeed);

        if (vdirection == "forward") {
            nao.motion.moveTo(vspeed, 0.0, 0.0);
        }
        if (vdirection == "backward") {
            nao.motion.moveTo(-vspeed, 0.0, 0.0);
        }
        if (vdirection == "left") {
            nao.motion.moveTo(0.0, -vspeed, 0.0);
        }
        if (vdirection == "right") {
            nao.motion.moveTo(0.0, vspeed, 0.0);
        }
        if (vdirection == "turnleft") {
            nao.motion.moveTo(0.0, 0.0, vspeed);
        }
        if (vdirection == "turnright") {
            nao.motion.moveTo(0.0, 0.0, -vspeed);
        }
    },
    move: function (vdirection, localSpeed, nonblocking) {

        var currentstate = nao.life.getState();
        console.log(currentstate);
        if (nonblocking) {

            nao.life.setState("interactive");
        }

        if (!localSpeed) {
            localSpeed = speed;
        }


        if (!vdirection) {
            vdirection = "forward";
        }

        vspeed = parseFloat(localSpeed);

        if (nonblocking) {
            if (vdirection == "forward") {
                nao.motion.moveTo(vspeed, 0.0, 0.0);
            }
            if (vdirection == "backward") {
                nao.motion.moveTo(-vspeed, 0.0, 0.0);
            }
            if (vdirection == "left") {
                nao.motion.moveTo(0.0, -vspeed, 0.0);
            }
            if (vdirection == "right") {
                nao.motion.moveTo(0.0, vspeed, 0.0);
            }
            if (vdirection == "turnleft") {
                nao.motion.moveTo(0.0, 0.0, vspeed/2);
            }
            if (vdirection == "turnright") {
                nao.motion.moveTo(0.0, 0.0, -vspeed/2);
            }
        } else {


            if (vdirection == "forward") {
                nao.motion.move(vspeed, 0.0, 0.0);
            }
            if (vdirection == "backward") {
                nao.motion.move(-vspeed, 0.0, 0.0);
            }
            if (vdirection == "left") {
                nao.motion.move(0.0, -vspeed, 0.0);
            }
            if (vdirection == "right") {
                nao.motion.move(0.0, vspeed, 0.0);
            }
            if (vdirection == "turnleft") {
                nao.motion.move(0.0, 0.0, vspeed);
            }
            if (vdirection == "turnright") {
                nao.motion.move(0.0, 0.0, -vspeed);
            }
        }
        
        if (vdirection == "stop") {
            nao.motion.stopMove();
        }

        if (nonblocking) {

            nao.life.setState("solitary");
        }

        // switch (vdirection) {
        //     case "forward": nao.motion.move(vspeed, 0.0, 0.0); break;
        //     case "backward": nao.motion.move(-vspeed, 0.0, 0.0); break;
        //     case "left": nao.motion.move(0.0, -vspeed, 0.0); break;
        //     case "right": nao.motion.move(0.0, vspeed, 0.0); break;
        //     case "turnleft": nao.motion.move(0.1, 0.0, vspeed); break;
        //     case "turnright": nao.motion.move(0.1, 0.0, -vspeed); break;
        //     case "stop": nao.motion.stopMove(); break;

        // }
        //nao.life.setState(currentstate);


    },
    stopMove: function (autoon) {


        nao.motion.stopMove();

    }



}