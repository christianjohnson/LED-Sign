var locations = [];
var infoBubble = null;
var infoBubbleMachine = null; 
var geocoder; 
var counter = 1;
var currMessage = 1;
var currMessagePre = 0;
var map;
var xmlhttp;
var list;
var limit = 75;
var messages;

$(document).ready(function() {
   ajaxInit(limit);
 });

function makeMarker(center, message){
  //map.setCenter(results[0].geometry.location);
  //Create the marker
  var marker = new google.maps.Marker({
      map: map,
      position: center,
      title: "Message"
  });
  //create the content for the infowindow
  var contentString = message;
  var infowindow = new google.maps.InfoWindow({
    content: contentString
  });
  var pair = [];
  pair.push(marker);
  pair.push(infowindow);
  pair.push(center);
  locations.push(pair);
  //If there is a current infowindow open close it
  if (infoBubble)
    infoBubble.close();
  //Set the current infowindow open to infoBubble
  infoBubble = infowindow;
  //infowindow.open(map,marker);
  //Listener to the marker click event
  google.maps.event.addListener(marker,'click',function(){
    if (infoBubble)
      infoBubble.close();
    infowindow.open(map,marker);
    infoBubble = infowindow;
  });
  //Listener to the close click event on the infobubble
  google.maps.event.addListener(infowindow,'closeclick',function(){
    infoBubble = null;
  });
}

function codeAddress(center, message){
  var flag = 0;
  for (var i=0;i<locations.length;i++)
    if (locations[i][2].equals(center))
      flag = 1;
  if (flag == 0){
    makeMarker(center,message);
  }
}

function addMessage(){
  for (var i=4;i>=0;i--){
    li = document.createElement('li');
    li.innerHTML = '"' + messages[i].message + '" - ' + messages[i].city + ', ' + messages[i].state;
    list.insertBefore(li,list.firstChild);
  }
  setTimeout('rotateMessages()',2000);
}

function rotateMessages(){
  $("#mess li:eq("+counter+")").fadeOut('slow', function(){
    if (++counter >= list.childNodes.length)
      counter = 1;
    do{ 
      currMessage=Math.floor(Math.random()*(messages.length-1) + 1)
    }
    while(currMessage == currMessagePre);
    currMessagePre = currMessage;
    var newMessage = '"' + messages[currMessage].message + '" - ' + messages[currMessage].city + ', ' + messages[currMessage].state;
    $(this).text(newMessage);
    $(this).fadeIn('slow');
  });
  setTimeout('rotateMessages()',2000);
}

function rotateBubbles(){
  if (!infoBubble){
    if (infoBubbleMachine)
      infoBubbleMachine.close();
    locations[counter][1].open(map,locations[counter][0]);
    infoBubbleMachine = locations[counter][1];
    map.setCenter(locations[counter][0].location);
    setTimeout('rotateBubbles()',2000);
    counter++;
    if (counter >= locations.length)
      counter = 0;
  }
}

function parseLocations(mess){
  messages = eval('(' + mess + ')');
  for(var i=0;i<messages.length;i++){
    var center = new google.maps.LatLng(messages[i].lat,messages[i].lon);
    codeAddress(center, messages[i].message);
  }
  addMessage();
}

function GetXmlHttpObject(){
  if (window.XMLHttpRequest){
    // code for IE7+, Firefox, Chrome, Opera, Safari
    return new XMLHttpRequest();
  }
  if (window.ActiveXObject){
    // code for IE6, IE5
    return new ActiveXObject("Microsoft.XMLHTTP");
  }
  return null;
}

function ajaxInit(limit){
  xmlhttp=GetXmlHttpObject();
  if (xmlhttp==null){
    alert ("Your browser does not support AJAX!");
    return;
  }
  var url="/locations?limit=" + limit;
  xmlhttp.open("GET",url,true);
  xmlhttp.onreadystatechange= function(){
    if (xmlhttp.readyState==4){
      parseLocations(xmlhttp.responseText);
    }
  };
  xmlhttp.send(null);
}

function initialize() {
  geocoder = new google.maps.Geocoder();
  var latlng = new google.maps.LatLng(38.959409,-97.998047);
  var myOptions = {
    zoom: 3,
    center: latlng,
    mapTypeId: google.maps.MapTypeId.HYBRID
  };
  list = document.getElementById("mess");
  map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  //setTimeout(rotateBubbles(),5000);
}
