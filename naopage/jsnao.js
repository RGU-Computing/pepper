console.log('Loading Js NAO...');
var jsnao = {
  t : null,
  sname : null,
  coords : { x: 0, y: 0},
  session : null,
  al_sys : null,
  al_tts : null,
  al_video : null,
  al_motion : null,
  al_posture : null,
  log_listener : null,
  log_level : 4,
  error : function(data) { console.log(data) },
  connect : function(address) {
    console.log('Create Session to : '+address);
    jsnao.session = new QiSession();
    jsnao.session.socket().on('connect', jsnao.connected);
    jsnao.session.socket().on('disconnect', jsnao.disconnected);
  },
  connected : function() {
    console.log('Session Connected.');
    jsnao.session.service("ALSystem").done(jsnao.init_system);
    jsnao.session.service("ALMotion").done(jsnao.init_motion);
    jsnao.session.service("ALVideoDevice").done(jsnao.init_video);
    jsnao.session.service("ALTextToSpeech").done(jsnao.init_tts);
    jsnao.session.service("ALRobotPosture").done(jsnao.init_posture);
  },
  init_tts : function(data) {
    jsnao.al_tts = data;
    jsnao.al_tts.getLanguage().done(function(data) { $('#imgLang').attr('src', jsnao.getLangImage(data)); });
    $('#DivTts').show(300);
    console.log('Text To Speech Initialized.');
  },
  init_system : function(data) {
    jsnao.al_sys = data;
    $('#DivSys').show(300);
    jsnao.al_sys.robotName().done(function(data) { $('#RbtName').text(data); $('#RbtName').show(300); });
    jsnao.al_sys.systemVersion().done(function(data) {
      $('#RbtVersion').text(data);
      $('#RbtVersion').show(300);
      if (data.indexOf('2.') == 0) {
        $('#DivLogs').show(300);
      }
    });
    jsnao.al_sys.robotIcon().done(function(data) { $('#RbtIcon').attr('src', 'data:image/png;base64,'+data); });
    console.log('System Initialized.');
  },
  init_motion : function(data) {
    jsnao.al_motion = data;
    $('#DivMotion').show(300);
    console.log('Motion Initialized.');
  },
  init_posture : function(data) {
    jsnao.al_posture = data;
    $('#DivPosture').show(300);
    console.log('Posture Initialized.');
  },
  init_video : function(data) {
    jsnao.al_video = data;
    $('#DivVideo').show(300);
    console.log('Video Initialized.');
  },
  level_logs: function(newLevel) {
    var new_level = 4;
    if (newLevel == undefined) {
      new_level = jsnao.log_level + 1;
      if (new_level > 6) {
        new_level = 1;
      }
    }
    jsnao.log_level = new_level;
    console.log('New Log Level = '+jsnao.log_level)
    if (jsnao.log_listener) {
      jsnao.log_listener.setVerbosity(jsnao.log_level);
      if (jsnao.logLevels.hasOwnProperty(jsnao.log_level)) {
        $('#LogLevel').text('Logger Level : '+jsnao.logLevels[jsnao.log_level].label);
      }
    }
  },
  display_logs: function() {
    $('#DivLogs').hide(300);
    $('#DivLogContainer').show(300);
    jsnao.session.service("LogManager").done(function(logMan) {
      console.log('LogManager Service Loaded');
      logMan.getListener().done(function(newListener) {
        console.log('LogListener Loaded');
        jsnao.log_listener = newListener;
        jsnao.log_listener.onLogMessage.connect(jsnao.add_log);
        jsnao.level_logs(4);
      });
    });
  },
  add_log: function(logData) {
    // If the Log Level is in the List
    if (jsnao.logLevels.hasOwnProperty(logData.level)) {
      var log_level = jsnao.logLevels[logData.level];
      var spanLvl = $('<span style="color:'+log_level.color+';margin-left:5px;">['+log_level.label+']</span>');
      var spanCat = $('<span style="color:#0094FF;margin-left:5px;">'+logData.category+' : </span>');
      var spanMsg = $('<span style="color:#000000;margin-left:5px;">'+logData.message+'</span>');
      var logLine=$('<div style="border-bottom: solid 1px #DCDCDC;"></div>');
      logLine.append(spanLvl);
      logLine.append(spanCat);
      logLine.append(spanMsg);
      $('#DivLogger').prepend(logLine);
    }
  },
  move_head : function() {
    var dx = jsnao.coords.x - ($("#myCanvas0").width() / 2);
    var dx = -dx / $("#myCanvas0").width() * 2.09;
    var dy = jsnao.coords.y - ($("#myCanvas0").height() / 2);
    var dy = dy / $("#myCanvas0").height() * 0.90;
    var v = 0.5
    jsnao.al_motion.angleInterpolation(['HeadYaw', 'HeadPitch'], [[dx], [dy]], [[v],[v]], true).done(jsnao.move_head).fail(jsnao.move_head);
  },
  display_video : function() {
    jsnao.al_motion.setStiffnesses('Head', 1.0).fail(jsnao.error);
    $('#BtnVid').hide(300);
    $('#DivVid1').show(300);
    $('#DivVid2').show(300);
    $("#myCanvas0").mousemove(function(e){
      jsnao.coords.x = e.pageX - $(this).offset().left;
      jsnao.coords.y = e.pageY - $(this).offset().top;
    });
    jsnao.move_head();
    jsnao.t = [];
    for (var i = 0; i < 1024; ++i) {
      jsnao.t[String.fromCharCode(i)] = i;
    }
    var z = Math.floor((Math.random()*10000)+1);
    jsnao.al_video.subscribeCameras("test_z" + z, [0,1], [0,0], [11,11], 30).done(jsnao.subscribed_video).fail(jsnao.error);
  },
  subscribed_video : function(sname) {
    jsnao.sname = sname;
    jsnao.al_video.getImagesRemote(jsnao.sname).done(jsnao.image_remote).fail(jsnao.error);
  },
  image_remote : function(data) {
    if (data.length > 0) {
      var imgData = data[0];
      if (imgData.length > 6) {
        var idCanvas = 'myCanvas0';
        var imgWidth = imgData[0];
        var imgHeight = imgData[1];
        var imgBase64 = imgData[6];
        jsnao.display_image(idCanvas, imgWidth, imgHeight, imgBase64);
      }
    }
    if (data.length > 1) {
      var imgData = data[1];
      if (imgData.length > 6) {
        var idCanvas = 'myCanvas1';
        var imgWidth = imgData[0];
        var imgHeight = imgData[1];
        var imgBase64 = imgData[6];
        jsnao.display_image(idCanvas, imgWidth, imgHeight, imgBase64);
      }
    }
    jsnao.al_video.getImagesRemote(jsnao.sname).done(jsnao.image_remote).fail(jsnao.error);
  },
  display_image : function(idCanvas, imgWidth, imgHeight, imgBase64) {
    var imgBin = atob(imgBase64);
    var x = 0;
    var w = imgWidth * imgHeight * 4;
    var canvas = document.getElementById(idCanvas);
    var context = canvas.getContext('2d');
    var imageData = context.getImageData(0, 0, imgWidth, imgHeight);
    for (var p = 0; p < w; ) {
      imageData.data[p++] = jsnao.t[imgBin[x++]];
      imageData.data[p++] = jsnao.t[imgBin[x++]];
      imageData.data[p++] = jsnao.t[imgBin[x++]];
      imageData.data[p++] = 255;
    }
    context.putImageData(imageData, 0, 0);
  },
  disconnected : function() {
    console.log('Session Disconnected.');
  },
  getLangImage : function(code_lang) {
    if (jsnao.languages.hasOwnProperty(code_lang)) {
      return jsnao.languages[code_lang].image;
    }
    return 'img/check.png';
  },
  logLevels : {
    1: {'label': 'FATAL',   'color': '#B200FF'},
    2: {'label': 'ERROR',   'color': '#FF0000'},
    3: {'label': 'WARN' ,   'color': '#FF6A00'},
    4: {'label': 'INFO',    'color': '#267F00'},
    5: {'label': 'VERBOSE', 'color': '#0026FF'},
    6: {'label': 'DEBUG',   'color': '#404040'}
  },
  languages : {
    'English':    { 'image' : 'img/flag_english.png' },
    'French':     { 'image' : 'img/flag_french.png' },
    'Italian':    { 'image' : 'img/flag_italian.png' },
    'Portuguese': { 'image' : 'img/flag_portuguese.png' },
    'German':     { 'image' : 'img/flag_german.png' },
    'Spanish':    { 'image' : 'img/flag_spanish.png' },
    'Japanese':   { 'image' : 'img/flag_japanese.png' },
    'Korean':     { 'image' : 'img/flag_korean.png' },
    'Chinese':    { 'image' : 'img/flag_chinese.png' },
    'Brazilian':  { 'image' : 'img/flag_brazilian.png' },
    'Turkish':    { 'image' : 'img/flag_turkish.png' },
    'Arabic':     { 'image' : 'img/flag_arabic.png' },
    'Polish':     { 'image' : 'img/flag_polish.png' },
    'Czech':      { 'image' : 'img/flag_czech.png' },
    'Dutch':      { 'image' : 'img/flag_dutch.png' },
    'Danish':     { 'image' : 'img/flag_danish.png' },
    'Finnish':    { 'image' : 'img/flag_finnish.png' },
    'Swedish':    { 'image' : 'img/flag_swedish.png' },
    'Russian':    { 'image' : 'img/flag_russian.png' },
    'Norwegian':  { 'image' : 'img/flag_norwegian.png' }
  }
}
console.log('Js NAO is loaded.');
