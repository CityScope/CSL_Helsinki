var f =0
var scenario=1
// var colScale=['#add8e6', '#a4c1db', '#9baad0' ,'#9194c5' ,'#877eb9', 
// '#7d68ae', '#7152a3', '#653c98' ,'#59248d', '#4b0082'];
// var colScale=['#ffffe5','#ffffe5','#fff7bc','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#993404','#662506'];
var chromaScale = chroma.scale(['#3182bd', '#fa9fb5', '#c51b8a']);
///////////// STYLE FUNCTIONS////////////

// function getColor(p) {
// 	if (p =='None'){return '#555555'}
// 	else{
//       	return p > 0.9 ? '#a50026' :
//           p > 0.8  ? '#d73027' :
//           p > 0.7  ? '#f46d43' :
//           p > 0.6  ? '#fdae61' :
//           p > 0.5   ? '#fee08b' :
//           p > 0.4   ? '#d9ef8b' :
//           p > 0.3   ? '#a6d96a' :
//           p > 0.2   ? '#66bd63' :
//                 '#1a9850';
// 	}
// 	}
function getColor(p) {
 if (p =='None'){return '#aaaaaa'}
 // else return colScale[Math.floor(p*10)]
 else return chromaScale(p)
 }

function getBldStyle(p, al, hubInd) {
      col=getColor(p)
      if (hubInd==1){
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
        };
      return options
    }

///////////// INITIALISE THE MAP////////////

var map = L.map('map').setView([60.187394, 24.832049], 15);
tile=L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
    subdomains: 'abcd',
    maxZoom: 19
    });
var Stamen_Toner = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.{ext}', {
  attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  subdomains: 'abcd',
  maxZoom: 19,
  ext: 'png'
});
var mapboxStreets=L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZG9vcmxleXJtaXQiLCJhIjoiY2pnNnh5NHJwOHp2YzJ4bXNkdWZyNWd3ZSJ9.am1Wub7LEzVfZKHAdRZe4g')
var mapboxCustom=L.tileLayer('https://api.mapbox.com/styles/v1/doorleyrmit/cjg6y59xi0ul82rqknbxm024p/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiZG9vcmxleXJtaXQiLCJhIjoiY2pnNnh5NHJwOHp2YzJ4bXNkdWZyNWd3ZSJ9.am1Wub7LEzVfZKHAdRZe4g')
mapboxCustom.addTo(map);


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
    legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
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
        container.style.textAlign='right';
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
    .defer(d3.json,'./prepared/building_usage.geojson')
    .defer(d3.json,'./prepared/data.json')
    .await(startAnimation);


});


function startAnimation(error, bldData, data) {  
  console.log('starting animation')
  connections=data.connections_Adhoc
  if (scenario==2){connections=data.connections_AdhocX;}
  times=data.times
  var looper = setInterval(function(){
  console.log(f)
  
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
        else {usageFeature='avgUsage_AdhocX'}
    if (usageFeature in bldData.features[i].properties)
      {d=bldData.features[i].properties[usageFeature][f]
        al=1}
    else
      {d='None'
      al=1}
    style=getBldStyle(d, al, hubInd)
    L.polygon(polyPoints,style).addTo(bldPolys);
  }

  if (scenario>0){
    for (l=0; l<connections[f].length; l++){
      if ((connections[f][l]['origin'].length>0)&&(connections[f][l]['destination'].length>0)){
        var pointA = new L.LatLng(connections[f][l]['origin'][1], connections[f][l]['origin'][0]);
        var pointB = new L.LatLng(connections[f][l]['destination'][1], connections[f][l]['destination'][0]);
        style={color: 'yellow',weight: 1+((connections[f][l]['num'])/5),opacity: 0.5}
        var polyline = new L.Polyline([pointA, pointB] ,style);
        var animatedMarker = L.animatedMarker(polyline.getLatLngs(), {'distance':25, 'interval':25, 'icon':icon});
        //polyline.addTo(lines);
        animatedMarker.addTo(markers);
      }
    }
  }
  


f+=1
if (f>=connections.length){clearInterval(looper)}
}, 1500)

}




   
    


  