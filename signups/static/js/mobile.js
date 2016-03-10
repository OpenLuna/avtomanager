var LEFT = 74; //j
var RIGHT = 76; //l
var UP = 73; //i
var DOWN = 75; //k
var ON = "ON";
var OFF = "OFF";
var WS_URL = "ws://" + window.location.href.split("/")[2].split(":")[0] + ":4113/";
var STREAM_URL = "http://" + window.location.href.split("/")[2].split(":")[0] + ":4114/stream.mjpg";
var HTTP_URL = "http://" + window.location.href.split("/")[2].split(":")[0] + ":8080/";

var keysdown = {};
var websocket = null;

var state = {up: false, down: false, left:false, right: false};

function keypressHandle(e){
	if(e.type == "keydown"){
		if(!keysdown[e.keyCode]){
			keysdown[e.keyCode] = true;
			sendState();
		}
	}
	else if(e.type == "keyup"){
		keysdown[e.keyCode] = false;
		sendState();
	}
	else console.error(e);
}

function sendState(){
	if(websocket != null){
		var cmd = "up=" + (state.up ? ON:OFF) + "&down=" + (state.down ? ON:OFF) + "&left=" + (state.left ? ON:OFF) + "&right=" + (state.right ? ON:OFF);
		console.log(cmd);
		websocket.send(cmd);
	}
}

function wsConnection(){
	if(websocket != null){
		websocket.close();
	}
	else{
		var token = 123;
		var query = encodeURI("token=" + token + "&name=RangeRover");
		websocket = new WebSocket(WS_URL);
		websocket.onopen = function(evt){
//			$("button#ws_connect").text("Disconnect");
			console.log("Connected to Range Rover");
			$("#stream").attr("src", encodeURI(STREAM_URL + "?token=" + token + "&name=RangeRover"));
			websocket.send(query);
		};
		
		websocket.onclose = function(evt){
//			$("button#ws_connect").text("Connect");
			console.log("Close reason: " + evt.reason);
			$("#stream").attr("src", "http://www.joomlaworks.net/images/demos/galleries/abstract/7.jpg");
			websocket = null;
//			refreshCarsList();
		};
		
		websocket.onmessage = function(evt){
			console.log(evt.data);
		};
		
		websocket.onerror = function(evt){
			$("#status").text("ERROR: " + evt);
			console.log(evt);
		};
	}
}

function refreshCarsList(){
	var URL = HTTP_URL + "cars_list";
	$.ajax({
		url: URL,
		success: function(data, textStatus, jqXHR){
			var html = "";
			data.forEach(function(d){
				html += "<option value='" + d + "'>" + d + "</option>";
			});
			$("select#cars_list").html(html);
		},
		error: function(jqXHR, status, error){
			console.log(status + " " + error);
		}
	});
}

function touch(evt){
	document.documentElement.webkitRequestFullscreen();
	screen.orientation.lock("landscape");
	if(websocket != null){
		if(evt.target.id != "ws_connect"){
			evt.preventDefault();
			var x = evt.originalEvent.changedTouches[0].pageX;
			
			if(evt.type == "touchstart"){ //touch
				if(x < window.innerWidth / 2) state.down = true;
				else state.up = true;
			}
			else{ //release
				if(x < window.innerWidth / 2) state.down = false;
				else state.up = false;
			}
			sendState();
		}
	}
}

function orientationHandle(e){
	//$("#orientout").html(e.alpha + "<br/>" + e.beta + "<br/>" + e.gamma + "<br />" + e.absolute);
	
	var delta = 20;
	var changed = false;
	
	if(e.beta < -delta){
		if(!state.left){
			state.left = true;
			changed = true;
		}
	}
	else if(e.beta > delta){
		if(!state.right){
			state.right = true;
			changed = true;
		}
	}
	else if(state.left || state.right){
		state.left = false;
		state.right = false;
		changed = true;
	}
	
	if(changed) sendState();
}

function motionHandle(e){
	//console.log(e.accelerationIncludingGravity.x + ", " + e.accelerationIncludingGravity.y);
	
	var delta = 2;
	var changed = false;
	var orient = e.accelerationIncludingGravity.y;
	
	if(orient < -delta){
		if(!state.left){
			state.left = true;
			changed = true;
		}
	}
	else if(orient > delta){
		if(!state.right){
			state.right = true;
			changed = true;
		}
	}
	else if(state.left || state.right){
		state.left = false;
		state.right = false;
		changed = true;
	}
	
	if(changed) sendState();
}

$(document).ready(function() {
	//window.addEventListener("deviceorientation", orientationHandle, false);
	window.addEventListener("devicemotion", motionHandle, false);
//	$(window).keydown(keypressHandle).keyup(keypressHandle);
	$(window).on("touchstart touchend", touch);
	wsConnection();
});
