window.onload = function () {
  index = 0
  var map = L.map('map',{
      minZoom: 2,
      maxZoom:6,

      }).setView(latlong[index], 5);

  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
      //the slider bar
      $('#button').bind('click', function(){
          $('#bar').animate({"width": '200'})
          var info = $("<div id = info><p>this is where info goes</p><p>I will make a 'slide back' option later</p></div>")
              .appendTo("#bar")
          console.log('click')

          })

        $('#but').bind('click', function(){
    console.log('click')
    $('.leaflet-popup-content-wrapper').css({'height':'700px'})
    $('#metadata-content').show()
  })

  //function chain for drawing the markers and lines on the map.
  
  delay = (500+timestamp_list[index]) //sets the animationspeed
  
  clusterGroups = {} //contains all country specific clusters

  makeClusterGroups(country_code_list, index) //initialize first cluster

  AddStep(latlong[index], latlong[index+1], index) // initialize the animation

  

  function makeClusterGroups(country_code_list, index){
    for (var i = 0; i < unique_country_code_list.length; i++){
      if (unique_country_code_list[i] == country_code_list[index]){
        if (clusterGroups[unique_country_code_list[i]]){
          //checks if a cluster for the country already exists
          return
        }
        else
          //if not make it.
          clusterGroups[unique_country_code_list[i]] = new L.MarkerClusterGroup();
      }
    }
  }

  //console.log(clusterGroups)
  function AddMarkerCluster(marker, index){
    clusterGroups[country_code_list[index]].addLayer(marker)
    map.addLayer(clusterGroups[country_code_list[index]])
  }

  function AddMarker(src, index){
    makeClusterGroups(country_code_list, index)
    var marker = L.marker([src[0], src[1]])
    var popup = L.Popup({
      maxHeight: 50})
    var popupcontent = "<p>Hop no:"+hop_list[index]+"<br /><div id='metadata' $(this).hide()><button id='but'>show metadata</button><div id='metadata-content'>Server name:<br />"+server_name_list[index]+"<br />Network owner:<br />"+asn_list[index]+"</div></div>"
    marker.bindPopup(popupcontent)
    AddMarkerCluster(marker, index)
  }

  function AddStep(src, dest, index){
  var b = new R.BezierAnim([src, dest], {})
  map.addLayer(b)
  AddMarker(src, index)
  //console.log('AddStepp'+index)
  processStep(index)
  //console.log(delay)
  }

  function processStep (index) {
    map.panTo(latlong[index]);
    if (index < counter_max-2) {
      //console.log('hop#', hop_list[index])
      changeFavicon('images/world/'+country_code_list[index]+'.png')
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index+1], index)
      //console.log('processStep')
     }, delay);}

    else
    if (index < counter_max-1){
    //console.log('hop#', hop_list[index])
    changeFavicon('images/world/'+country_code_list[index]+'.png')
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index], index)
     }, delay);}

    else
    if (index = counter_max-1){
      changeFavicon('images/world/'+country_code_list[index]+'.png')
      //console.log('fin')
      //map.fitBounds([bounds])
    }

    index = index + 1
    delay = (500 + timestamp_list[index])
    }
$('.leaflet-marker-icon').bind('click', function(){
  console.log('clickkkk')
})
};

