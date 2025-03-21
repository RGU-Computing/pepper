var slider;
var output;
var speed = 0.1;
var coords = {
    x: 0,
    y: 0
};
var t;
var sname;

$(document).ready(function () {
    console.log("page ready");
//this might be the problem running direct
    nao.init("localhost");

    $('#DivTts').show(300);
    $('#DivSys').show(300);
    $('#DivMotion').show(300);
    $('#DivPosture').show(300);
    $('#DivVideo').show(300);

    $('#RbtSay').keyup(function (e) {
        if (e.keyCode == 13 /* Enter */) {
            var configuration = {
                "bodyLanguageMode": "contextual"
            };
            nao.animatedSay.say($('#RbtSay').val(), configuration);
            $('#RbtSay').val("")

        }
    });

    $('#RbtSay2').keyup(function (e) {
        if (e.keyCode == 13 /* Enter */) {
            var configuration = {
                "bodyLanguageMode": "contextual"
            };
            nao.animatedSay.say($('#RbtSay2').val(), configuration);
            //$('#RbtSay').val("")

        }
    });

    $('#RbtSay3').keyup(function (e) {
        if (e.keyCode == 13 /* Enter */) {
            var configuration = {
                "bodyLanguageMode": "contextual"
            };
            nao.animatedSay.say($('#RbtSay3').val(), configuration);
            //$('#RbtSay').val("")

        }
    });
    slider = $('#speedSlider');
    output = $('#demo');
    output.innerHTML = slider.value; // Display the default slider value
    // Update the current slider value (each time you drag the slider handle)
    slider.change(function () {

        nao.speed = parseFloat(this.value) / 10;
        speed = parseFloat(this.value) / 10;
        console.log(nao.speed);
        output.innerHTML = this.value;
    });

    $('#image').keyup(function (e) {
        if (e.keyCode == 13 /* Enter */) {
            displayImage($('#image').val());
        }
    });

    


});




function move_head() {
    var dx = coords.x - ($("#myCanvas0").width() / 2);
    var dx = -dx / $("#myCanvas0").width() * 2.09;
    var dy = coords.y - ($("#myCanvas0").height() / 2);
    var dy = dy / $("#myCanvas0").height() * 0.90;
    var v = 0.5
    var names = ['HeadYaw', 'HeadPitch'];
    var angles = [dx, dy];
    var times = [v, v];

    nao.motion.angleInterpolation(names, angles, times, true).then(move_head)
}

function displayVideo() {
    nao.motion.setStiffnesses('Head', 1.0)
    $('#BtnVid').hide(300);
    $('#DivVid1').show(300);
    $('#DivVid2').show(300);
    $("#myCanvas0").mousemove(function (e) {
        coords.x = e.pageX - $(this).offset().left;
        coords.y = e.pageY - $(this).offset().top;
    });
    move_head();
    t = [];
    for (var i = 0; i < 1024; ++i) {
        t[String.fromCharCode(i)] = i;
    }
    var z = Math.floor((Math.random() * 10000) + 1);
    nao.video.subscribeCameras("test_z" + z, [0, 1], [0, 0], [11, 11], 30).then(subscribed_video)
}

function subscribed_video(name) {
    sname = name;

    nao.video.getImagesRemote(sname).then(image_remote)

}

function image_remote(data) {
    //console.log(data);
    if (data.length > 0) {
        var imgData = data[0];
        if (imgData.length > 6) {
            var idCanvas = 'myCanvas0';
            var imgWidth = imgData[0];
            var imgHeight = imgData[1];
            var imgBase64 = imgData[6];
            display_image(idCanvas, imgWidth, imgHeight, imgBase64);
        }
    }
    if (data.length > 1) {
        var imgData = data[1];
        if (imgData.length > 6) {
            var idCanvas = 'myCanvas1';
            var imgWidth = imgData[0];
            var imgHeight = imgData[1];
            var imgBase64 = imgData[6];
            display_image(idCanvas, imgWidth, imgHeight, imgBase64);
        }
    }
    nao.video.getImagesRemote(sname).then(image_remote)
}

function display_image(idCanvas, imgWidth, imgHeight, imgBase64) {
    // var imgBin = window.atob(imgBase64);
    // //var imgBin = imgBase64;
    // var x = 0;
    // var w = imgWidth * imgHeight * 4;
    // var canvas = document.getElementById(idCanvas);
    // var context = canvas.getContext('2d');
    // var imageData = context.getImageData(0, 0, imgWidth, imgHeight);
    // for (var p = 0; p < w;) {
    //     imageData.data[p++] = t[imgBin[x++]];
    //     imageData.data[p++] = t[imgBin[x++]];
    //     imageData.data[p++] = t[imgBin[x++]];
    //     imageData.data[p++] = 255;
    // }
    // context.putImageData(imageData, 0, 0);

    // // Obtain a blob: URL for the image data.
    // var arrayBufferView = new Uint8Array( imgBase64 );
    // var blob = new Blob( imgBase64, { type: "image/jpeg" } );
    // var urlCreator = window.URL || window.webkitURL;
    // var imageUrl = urlCreator.createObjectURL( blob );
    // var img = document.querySelector( "#photo" );
    // img.src = imageUrl;
    var canvas = document.getElementById(idCanvas);



    var ctx = canvas.getContext('2d');

    var drawArray = function (arr, width, height) {
        // set your canvas width/height
        canvas.width = width;
        canvas.height = height;

        // create the imageData object, you'll need the width and height of your image
        var dataImage = ctx.createImageData(width, height);
        // browsers supporting TypedArrays
        if (dataImage.data.set) {
            dataImage.data.set(arr);
        } else {
            // IE9
            arr.forEach(function (val, i) {
                dataImage.data[i] = val;
            });
        }
        ctx.putImageData(dataImage, 0, 0);
    };


    drawArray(imgBase64, imgWidth, imgHeight);
}

function selectBehaviour() {
    document.getElementById("myDropdown").classList.toggle("show");
    //getBehaviours();


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
        nao.behaviourManager.runBehavior(data[b]);

    });

}

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
  }

function getBehaviours() {
    console.log("getBehaviours")
    nao.behaviourManager.getInstalledBehaviors().then(function (data) {
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
            nao.behaviourManager.runBehavior($(this)[0].innerText);
        })

    })
}

function runBehaviour(behaviour) {
    nao.behaviourManager.runBehavior(behaviour);
}

function stopAll() {
    nao.behaviourManager.stopAllBehaviors();
}

function randomHello() {

    var rnd = Math.floor(Math.random() * 4);

    switch (rnd) {
        case 0:
            nao.animatedSay.say("Hello!");
            break;
        case 1:
            nao.animatedSay.say("Hi!");
            break;
        case 2:
            nao.animatedSay.say("Hi There!");
            break;
        case 3:
            nao.animatedSay.say("Nice to see you!");
            break;
        default:
            nao.animatedSay.say("Hello!");
            break;
    }
}

function displayImage(image) {
    nao.tablet.showImage(image);
}