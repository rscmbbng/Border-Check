window.onload = function () {
  var map = L.map('map',{
      minZoom: 2,
      maxZoom:5,

      }).setView([38.0, -97.0], 3);

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

  //function chain for drawing the markers and lines on the map.
  index = 0
  delay = (400+timestamp_list[index])

  AddStep(latlong[index], latlong[index+1], index)

  function AddMarker(src, index){
  var marker = L.marker([src[0], src[1]]).bindPopup(
    "<p>Hop no:"+hop_list[index]+"<br /><a>show metadata</a></p><p id=metadata'>Server name:<br />"+server_name_list[index]+"<br />Network owner:<br />"+asn_list[index]+"</p>"
    );
  marker.addTo(map).openPopup()
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
};

