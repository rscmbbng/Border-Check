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
  
  delay = (400+timestamp_list[index])
  clusterGroup = new L.MarkerClusterGroup();
  AddStep(latlong[index], latlong[index+1], index)
  

  function AddMarkerCluster(marker, index){
    clusterGroup.addLayer(marker)
  }
  function AddMarker(src, index){
  var marker = L.marker([src[0], src[1]])
  var popup = L.Popup({
      maxHeight: 50})
  var popupcontent = "<p>Hop no:"+hop_list[index]+"<br /><div id='metadata' $(this).hide()><button id='but'>show metadata</button><div id='metadata-content'>Server name:<br />"+server_name_list[index]+"<br />Network owner:<br />"+asn_list[index]+"</div></div>"
  marker.bindPopup(popupcontent)
  //marker.addTo(map).openPopup()
   $('#metadata-content').hide()
   AddMarkerCluster(marker)
   map.addLayer(clusterGroup)
  }

  function AddStep(src, dest, index){
  var b = new R.BezierAnim([src, dest], {})
  map.addLayer(b)
  AddMarker(src, index)
  processStep(index)
  //console.log(delay)
  }

  function processStep (index) {
    map.panTo(latlong[index]);
    if (index < counter_max-2) {
      //console.log('hop#', hop_list[index])
      changeFavicon('js/world/'+country_code_list[index]+'.png')
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index+1], index)
     }, delay);}
    else
    if (index < counter_max-1){
    //console.log('hop#', hop_list[index])
    changeFavicon('js/world/'+country_code_list[index]+'.png')
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index], index)
     }, delay);}

    else
    if (index = counter_max-1){
      changeFavicon('js/world/'+country_code_list[index]+'.png')
      //console.log('fin')
      //map.fitBounds([bounds])
      
    }

    index = index + 1
    delay = (400 + timestamp_list[index])
    }
$('.leaflet-marker-icon').bind('click', function(){
  console.log('clickkkk')
})
};

