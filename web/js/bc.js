window.onload = function () {
  index = 0
  cables = L.tileLayer('http://{s}.tiles.mapbox.com/v3/rllfff.Test/{z}/{x}/{y}.png',{
    attribution: 'Cable data: <a href="http://cablemap.info/">cablemap.info</a>'
  })
  blank_map = L.tileLayer('http://{s}.tiles.mapbox.com/v3/rllfff.blank-populations/{z}/{x}/{y}.png')
  osm =   L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  })
  var map = L.map('map',{
      minZoom: 2,
      maxZoom:6,
      zoomControl:false,
      layers: [blank_map]
      }).setView(latlong[index], 3);

  blank_map.addTo(map)

  var baseMaps = {
    "Submarine cables": cables,
    "OSM default": osm,
    "Blank map": blank_map
  }


 //setting the controls:
  new L.control.layers(baseMaps, null, {collapsed:false}).addTo(map)
  new L.Control.Zoom({
    position: 'topright'}
    ).addTo(map)
  new L.Control.Attribution

  //custom markers:




      //the slider bar
      $('.info').hide()
      slide = 0 
      $('#button').bind('click', function(){
        if (slide == 0){
          $('.bar').animate({"width": '300'})
          $('.info').show()
          $('#button').html('<')
            }

        slide += 1

        if (slide == 2){
          $('.bar').animate({"width": '20'})
          $('.info').hide()
          $('#button').html('>')
          slide = 0}
      })

      $('#attrib-content').hide()
      $('#about-content').hide()
      $('#contact-content').hide()

      $('#attrib').bind('click', function(){
      $('#attrib-content').toggle(400)})

      $('#legend').bind('click', function(){
      $('#legend-content').toggle(400)})

      $('#about').bind('click', function(){
      $('#about-content').toggle(400)})

      $('#contact').bind('click', function(){
      $('#contact-content').toggle(400)})

      //legend controlls
        $('#home').bind('click', function(){
        $('#legend-text').html("This is the first hop on your journey, most probably your provider's router in your street or neighbourhood")})
        $('#hop').bind('click', function(){
        $('#legend-text').html('This represents either a server or router that you pass. Click it to get metadata on it.')})
        $('#cluster').bind('click', function(){
        $('#legend-text').html('Server hops in the same country or location get automatically grouped into clusters. Click the clusters to see individual hops.')})
        $('#destination').bind('click', function(){
        $('#legend-text').html("The last hop on your journey. Ideally it is the machine that serves the destination website. More likeley however it is it's firewall")})






  //function chain for drawing the markers and lines on the map.
  
  delay = (100+timestamp_list[index]) //sets the animationspeed
  
  clusterGroups = {} //contains all country specific clusters

  makeClusterGroups(country_code_list, index) //initialize first cluster

  AddStep(latlong[index], latlong[index+1], index) // initialize the animation

  function makeCustomMarker(index){
    if (index < counter_max){
      var customIcon = new L.icon({
      iconUrl: 'images/markers/marker-icon-'+index+'.png',

      iconSize:     [30, 30], // size of the icon
      iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
      popupAnchor:  [-150, 50] // point from which the popup should open relative to the iconAnchor
      });
    }
    if (index == counter_max){
      var customIcon = new L.icon({
      iconUrl: 'images/markers/marker-icon-last.png',

      iconSize:     [30, 30], // size of the icon
      iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
      popupAnchor:  [-150, 0] // point from which the popup should open relative to the iconAnchor
      });
    }
    return customIcon
}

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
    console.log(index)
    var marker = L.marker([src[0], src[1]],{icon: makeCustomMarker(index)})
    var popup = L.Popup({
      maxHeight: 50})
    var popupcontent = "Server name:<br /><b>"+server_name_list[index]+"</b><br />ASN: <br /><b>"+asn_list[index]+"</b><br />Network owner:<br /><b><a href='https://duckduckgo.com/?q="+telco_list[index]+"'>"+telco_list[index]+"</a></b></p>"
    marker.bindPopup(popupcontent)
    AddMarkerCluster(marker, index)
  }

  function AddStep(src, dest, index){
      var b = new R.BezierAnim([src, dest])
      map.addLayer(b)
      AddMarker(src, index)
      //console.log('AddStepp'+index)
      if (index < counter_max){
        map.panTo(latlong[index+1],{
          animate: true,
          duration: 2
          })}

      else
      if (index = counter_max){
        map.panTo(latlong[index],{
        animate: true,
        duration: 2
        }


        )
      }
    
    window.setTimeout(function(){
      processStep(index)
    }, 2000)

    //console.log(delay)
    }

  function processStep (index) {
    if (index < counter_max-1) {
      //console.log('hop#', hop_list[index])
      changeFavicon('images/world/'+country_code_list[index]+'.png')
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index+1], index)
      //console.log('processStep')
     }, delay);}

    else
    if (index < counter_max){
     // map.panTo(latlong[index+1]);
    //console.log('hop#', hop_list[index])
    changeFavicon('images/world/'+country_code_list[index]+'.png')
      window.setTimeout(function () {
      AddStep(latlong[index], latlong[index], index)
     }, delay);}

    else
    if (index = counter_max){
    //  map.panTo(latlong[index]);
      changeFavicon('images/world/'+country_code_list[index]+'.png')
      console.log('fin')
      //map.fitBounds([bounds])
    }

    index = index + 1
    delay = (100 + timestamp_list[index])
    }
$('.leaflet-marker-icon').bind('click', function(){
  console.log('clickkkk')
})
};

