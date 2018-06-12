var f =0
var scenario=3
var showCircles=1
var showLines=1
var hourInterval=2000
var showBounds=0
var outLines=0
var showHubs=0
var minTimer=0
// var colScale=['#add8e6', '#a4c1db', '#9baad0' ,'#9194c5' ,'#877eb9', 
// '#7d68ae', '#7152a3', '#653c98' ,'#59248d', '#4b0082'];
// var colScale=['#ffffe5','#ffffe5','#fff7bc','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#993404','#662506'];
var chromaScale = chroma.scale(['#62B1F6', '#DB70DB','#2E0854']);
///////////// STYLE FUNCTION////////////

function getColor(p) {
 if (p =='None'){return '#aaaaaa'}
 // else return colScale[Math.floor(p*10)]
 else return chromaScale(p)
 }

function getBldStyle(p, al, hubInd, showHubs) {
  if (showHubs==1){
    if (hubInd==1){col='firebrick'}
      else if (p=='None'){col='#aaaaaa'}
        else {col='blue'}
  var options = {
      fillColor: col,
      color: col,
      opacity: al,
      fillOpacity:al
      };}
  
  else{
    col=getColor(p)
    if (hubInd==1 & outLines==1){
      outCol='black'
      outAl=2
    }
      else {
        outCol=col
        outAl=al
      }
    var options = {
      fillColor: col,
      color: outCol,
      opacity: outAl,
      fillOpacity:al
      };}
    return options
    }

///////////// INITIALISE THE MAP////////////

var map = L.map('map').setView([60.186, 24.8055], 15);
var positron=L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
    subdomains: 'abcd',
    maxZoom: 19
    });

// var mapboxStreets=L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZG9vcmxleXJtaXQiLCJhIjoiY2pnNnh5NHJwOHp2YzJ4bXNkdWZyNWd3ZSJ9.am1Wub7LEzVfZKHAdRZe4g')
// var mapboxCustom=L.tileLayer('https://api.mapbox.com/styles/v1/doorleyrmit/cjg81wcd800182roee1115emw/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZG9vcmxleXJtaXQiLCJhIjoiY2pnNnh5NHJwOHp2YzJ4bXNkdWZyNWd3ZSJ9.am1Wub7LEzVfZKHAdRZe4g')
positron.addTo(map);


var bldPolys=L.featureGroup().addTo(map);
var lines=L.featureGroup().addTo(map);
var markers=L.featureGroup().addTo(map);

///////////// DEFINE THE ANIMATED ICONS////////////

var icon = L.divIcon({
    iconSize: [15, 15],
    iconAnchor: [10, 10],
    popupAnchor: [10, 0],
    shadowSize: [0, 0],
    className: 'animated-icon my-icon-id' 
})



///////////// DEFINE THE CUSTOM CONTROLS////////////
// Legend
// var legend = L.control({position: 'topright'});

// legend.onAdd = function (map) {
//     var div = L.DomUtil.create('div', 'info legend'),
//         grades = [0, 0.10, 0.20, 0.30, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
//         labels = ['<strong> % Occupancy </strong>'];
//     // loop through our occupancy intervals and generate a label with a colored square for each interval
//     for (var i = 0; i < grades.length; i++) {
//         div.innerHTML +=
//             '<i style="background:' + getColor(grades[i]+0.01) + '"></i> ' +
//             grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
//     }
//     return div;
// };
var legend = L.control({position: 'topright'});
if (showHubs==1){
    legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend');

    categories = ['Hubs','Resources'];
    hubCols=['firebrick', 'blue'];

    for (var i = 0; i < categories.length; i++) {
        div.innerHTML +=
            '<i style="background:' + hubCols[i] + '"></i> ' +
             (categories[i] ? categories[i] + '<br>' : '+');
    }

    return div;
        };
}
else {  
    legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0,20, 40, 60, 80],
        labels = ['<strong> % Occupancy </strong>'],
        from, to;

    for (var i = 0; i < grades.length; i++) {
        from = grades [i];
        to = grades[i+1];

    labels.push(
        '<i style="background:' + getColor(from/100 + 0.01) + '"></i> ' +
        from + (to ? '&ndash;' + to : '+'));
        }
        div.innerHTML = labels.join('<br>');
        return div;
        };
}
legend.addTo(map);

// Day and Time box
var timeControl = L.Control.extend({
		  options: {
		    position: 'bottomright' 
		    //control position - allowed: 'topleft', 'topright', 'bottomleft', 'bottomright'
		  },		 
		  onAdd: function (map) {
		    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
        container.id='timeID'
		    container.style.backgroundColor = 'transparent';
        container.style.color = 'white';
		    container.style.width = '300px';
		    container.style.height = '40px';
        container.style.border='none';
        container.style.fontSize='30px';
        container.style.textAlign='left';
		    return container;
		  },
		 
		});

map.addControl(new timeControl());
document.getElementById("timeID").style.fontFamily = "Helvetica, Arial, sans-serif";
// timeControl = document.getElementById("timeID");

// // Title
// var titleControl = L.Control.extend({
//       options: {
//         position: 'topright' 
//         //control position - allowed: 'topleft', 'topright', 'bottomleft', 'bottomright'
//       },     
//       onAdd: function (map) {
//         var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
//         container.id='titleID'
//         container.style.backgroundColor = 'transparent';
//         container.style.color = 'black';
//         container.style.width = '900px';
//         container.style.height = '60px';
//         container.style.border='none';
//         container.style.fontSize='50px';
//         return container;
//       },
     
//     });
// map.addControl(new titleControl());
// ttlControl = document.getElementById("titleID");
// if (scenario==0) {ttlControl.innerHTML='Baseline'}
//   else if (scenario==1) {ttlControl.innerHTML='Ad-hoc Sharing'}
//     else if (scenario==2) {ttlControl.innerHTML='50% More Students'}

/////////////////////DRAWING THE MAP IN AN ANIMATION////////////

$(document).ready(function(){
  
  queue()
    .defer(d3.json,'./prepared/building_usageSch.geojson')
    .defer(d3.json,'./prepared/dataSch.json')
    .defer(d3.json,'./prepared/bounds.geojson')
    .await(startAnimation);


});


function startAnimation(error, bldData, data, bounds) {  
  console.log('starting animation')
  if (scenario==1){connections=data.connections_Adhoc}
  else if (scenario==2){connections=data.connections_AdhocX;}
  else if (scenario==3){connections=data.connections_AdhocXSch;}
  if (minTimer==1) times=data.timesMin
  else times=data.times
  var looper = setInterval(function(){
  console.log(f)


  if (f==0 & showBounds==1){
      for (i=0;i<bounds.features.length; i++){
        var polyPoints=[]
        for (p=0; p< bounds.features[i].geometry.coordinates.length-1; p++){
            for (q=0; q< bounds.features[i].geometry.coordinates[p].length; q++){
            point=new L.LatLng(bounds.features[i].geometry.coordinates[p][q][1], bounds.features[i].geometry.coordinates[p][q][0])
            polyPoints.push(point);
        }
        }
      L.polygon(polyPoints, {'fillOpacity' : 0}).addTo(map);
    }
  }

  
  bldPolys.clearLayers()
  lines.clearLayers()
  markers.clearLayers()
  

  $("#timeID").html(times[f]);
    
  for (i=0;i<bldData.features.length; i++){
    var polyPoints=[]
    if (scenario>0) {hubInd=bldData.features[i].properties.Hub}
      else {hubInd=0}
    
    for (p=0; p< bldData.features[i].geometry.coordinates[0].length; p++){
      point=new L.LatLng(bldData.features[i].geometry.coordinates[0][p][1], bldData.features[i].geometry.coordinates[0][p][0])
      polyPoints.push(point);
    }
    if (scenario==0){usageFeature='avgUsage'}
      else if (scenario==1){usageFeature='avgUsage_Adhoc'}
        else if (scenario==2){usageFeature='avgUsage_AdhocX'}
          else usageFeature='avgUsage_AdhocXSch'
    if (usageFeature in bldData.features[i].properties)
      {d=bldData.features[i].properties[usageFeature][f]
        al=1}
    else
      {d='None'
      al=1}
    style=getBldStyle(d, al, hubInd, showHubs)
    L.polygon(polyPoints,style).addTo(bldPolys);
  }

  if (scenario>0 & showCircles==1){
    for (l=0; l<connections[f].length; l++){
      if ((connections[f][l]['origin'].length>0)&&(connections[f][l]['destination'].length>0)){
        var pointA = new L.LatLng(connections[f][l]['origin'][1], connections[f][l]['origin'][0]);
        var pointB = new L.LatLng(connections[f][l]['destination'][1], connections[f][l]['destination'][0]);
        style={color: 'yellow',weight: 1+((connections[f][l]['num'])/5),opacity: 0.5}
        var polyline = new L.Polyline([pointA, pointB] ,style);        
        var animatedMarker = L.animatedMarker(polyline.getLatLngs(), {'distance':25, 'interval':25, 'icon':icon});
        if (showLines==1) polyline.addTo(lines);
        animatedMarker.addTo(markers);
      }
    }
  }
  


f+=1
if (f>=connections.length){clearInterval(looper)}
}, hourInterval)

}




   
    


  