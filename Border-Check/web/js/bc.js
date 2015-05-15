var map;
function initMap () {
    index = 0
    stop_anim = false
    run_anim = false
    cables = L.tileLayer('http://{s}.tiles.mapbox.com/v3/rllfff.Test/{z}/{x}/{y}.png',{
	attribution: 'Cable data: <a href="http://cablemap.info/">cablemap.info</a>'
    })
    blank_map = L.tileLayer('http://{s}.tiles.mapbox.com/v3/rllfff.blank-populations/{z}/{x}/{y}.png')
//    osm = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
//	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
//    })
//    osm_quest = L.tileLayer('http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png')
    osm_sat = L.tileLayer('http://otile1.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.png')
//    streets = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
//    light = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.light/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
    dark = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.dark/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
//    comic = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.comic/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
//    pirates = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.pirates/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
//    high_contrast = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.high-contrast/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')
//    emerald = L.tileLayer('http://api.tiles.mapbox.com/v4/mapbox.emerald/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoicmxsZmZmIiwiYSI6IkZyVmt4bUUifQ.R--ZDzdb-672Dx1E3suO9A')

    map = L.map('map',{
	minZoom: 2,
	maxZoom:6,
	zoomControl:false,
	layers: [blank_map]
    });
    if (typeof latlong !== 'undefined') {
	map.setView(latlong[index], 3)
    }
    blank_map.addTo(map)
//    osm_sat.addTo(map)
    
    var baseMaps = {
	"Submarine cables": cables,
//	"Streets": streets,
//	"Emerald": emerald,
//	"Light": light,
//	"High-Contrast": high_contrast,
//	"Comic": comic,
//	"Pirates": pirates,
//	"OSM Blank": osm,
//	"OSM Geopolitical": osm_quest,
	"OSM Satellite": osm_sat,
        "Dark": dark,
	"Blank map": blank_map
    }
    
    //setting the controls:
    new L.control.layers(baseMaps, null, {collapsed:false}).addTo(map)
    
    new L.Control.Zoom({position: 'topright'}).addTo(map)
    
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
	$('#attrib-content').toggle(400)
    })
    
    $('#legend').bind('click', function(){
	$('#legend-content').toggle(400)
    })

    $('#about').bind('click', function(){
	$('#about-content').toggle(400)
    })

    $('#contact').bind('click', function(){
	$('#contact-content').toggle(400)
    })

    $('#form-submit').bind('click',function(){
//	console.log("loading "+$('#form-host').val())
	$('#form-target').load('http://127.0.0.1:8080/ajax?hostname='+$('#form-host').val())
    })

    $('#form-stop-anim').bind('click',function(){
//	console.log("stopping animation ")
	bcHistory.stop()
    })
    
    // legend controls
    $('#home').bind('click', function(){
        $('#legend-text').html("This is the first hop on your journey, most probably the router of your provider for your neighbourhood or city.")
    })

    $('#hop').bind('click', function(){
        $('#legend-text').html("This represents a hop to either a server or router that you pass. Click on it to view it's metadata." )
    })

    $('#cluster').bind('click', function(){
        $('#legend-text').html('Server hops in the same country or location get automatically grouped into clusters. Click the clusters to see individual hops.')
    })

    $('#destination').bind('click', function(){
        $('#legend-text').html("The last hop on your journey. Ideally it is the machine that serves the destination website. More likeley however it is it's firewall")
    })

    $('#error').bind('click',function(){
	$('#error').html('')
    })

    if(cur_url !== ""){
	bcHistory.play(cur_url)
	map.addControl(bcControl)
	//  add content : 
	//	$('.bc-custom-control').html("Hallo Welt")
	$('.bc-custom-control').hide();
    }
}

window.setInterval("watchUrl()",2000)

function watchUrl(){
    $('#form-target').load('http://127.0.0.1:8080/ajax')
}
