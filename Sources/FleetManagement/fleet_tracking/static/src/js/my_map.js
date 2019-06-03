var macarte = null;
var colors = new Array();

function initMap(id_div, centerPoint) {
    macarte = L.map(id_div).setView([centerPoint.lat, centerPoint.lng], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        minZoom: 1,
        maxZoom: 30
    }).addTo(macarte);
}

function genColor() {
    var current_color;
    do{
        r = Math.floor(Math.random()*255);
        g = Math.floor(Math.random()*255);
        b = Math.floor(Math.random()*255);
        current_color='rgb('+r+','+g+','+b+')';
    }while(current_color in colors);
    colors.push(current_color);
    return current_color;
}

function createWebSocket(url_server){
    var socket = null;
    try {
        index = url_server.indexOf(':') - 1;
        if (url_server.charAt(index) === 's'){
            socket = new WebSocket("wss://"+url_server.substring(index+4, url_server.length)+"/api/socket");
        }
        else{
            socket = new WebSocket("ws://"+url_server.substring(index+4, url_server.length)+"/api/socket");
        }
    } catch (exception) {
        console.log("erreur 1")
        console.error(exception);
    }

    return socket;
}