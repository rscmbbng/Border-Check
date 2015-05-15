function  bcHistoryEntry(hn,data){
    this.hn=hn
    this.data=data
    this.follow=false
    data=this.data
    this.counter_max =data[0]
    this.latlong =data[1]
    this.asn_list =data[2]
    this.hop_ip_list=data[3]
    this.telco_list =data[4]
    this.server_name_list =data[5]
    this.timestamp_list =data[6]
    this.country_code_list =data[7]
    this.unique_country_code_list =data[8]
    this.drawnLayers = new Array()
    this.index=0
    console.log("history entry for "+hn)

    this.state='hidden'
    this.speed= 1000 // animation speed in ms
    //    console.log(data)

    this.show=function(){
	if(this.state==='hidden'){
	    this.state='playing'
	    this.stop_anim=false
	    this.follow=true
//	    console.log("showing "+this.hn + " state " + this.state )
	    this.drawMarker()
	    $("#status").html("Travelling to :")
	    $("#url").html(this.hn)
	    $(".header").show()
	}
    }

    this.makeLink = function(){
	link= '<center>'
        +'<h2>'+this.hn+' '
	if(this.state=='hidden')
	    link =link +'  <a href="#" title="play" onclick="bcHistory.play(\''+this.hn+'\')"><img src="images/play.png"/></a>'
	if(this.state=='playing')
	    link =link +'  <a href="#" title="stop" onclick="bcHistory.stop(\''+this.hn+'\')"><img src="images/stop.png"/></a>'
	if(this.state=='show')
	    link =link +'  <a href="#" title="hide" onclick="bcHistory.hide(\''+this.hn+'\')"><img src="images/hide.png"/></a>'
	link =link+'  <a href="#" title="remove" onclick="bcHistory.remove(\''+this.hn+'\')"><img src="images/close.png"/></a>'
            +'</h2></center>'
	return link
    }
    
    this.drawMarker=function(){
	$("#url").html(this.hn)
	this.index=0
	this.delay = (100+this.timestamp_list[this.index]) //sets the animationspeed
	this.clusterGroups = {} //contains all country specific clusters
	this.makeClusterGroups(this.country_code_list) //initialize first cluster
	this.addStep() // initialize the animation
    }
    
    this.makeCustomMarker= function(){
	if (this.index < this.counter_max){
	    var customIcon = new L.icon({
		iconUrl: 'images/markers/marker-icon-'+this.index+'.png',
		
		iconSize:     [30, 30], // size of the icon
		iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
		popupAnchor:  [-150, 50] // point from which the popup should open relative to the iconAnchor
	    });
	}
	if (this.index == this.counter_max){
	    var customIcon = new L.icon({
		iconUrl: 'images/markers/marker-icon-last.png',
		iconSize:     [30, 30], // size of the icon
		iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
		popupAnchor:  [-150, 0] // point from which the popup should open relative to the iconAnchor
	    });
	}
	return customIcon
    }
    
    this.makeClusterGroups=function(country_code_list){
	for (var i = 0; i < this.unique_country_code_list.length; i++){
	    if (this.unique_country_code_list[i] == this.country_code_list[this.index]){
		if (this.clusterGroups[this.unique_country_code_list[i]]){
		    //checks if a cluster for the country already exists
		    return
		}
		else
		    //if not make it.
		    this.clusterGroups[this.unique_country_code_list[i]] = new L.MarkerClusterGroup();
	    }
	}
    }
    

    this.AddMarkerCluster=  function(marker){
	this.clusterGroups[this.country_code_list[this.index]].addLayer(marker)
	map.addLayer(this.clusterGroups[this.country_code_list[this.index]])
	this.drawnLayers.push(this.clusterGroups[this.country_code_list[this.index]])
    }
    
    this.AddMarker   =function(src){
	this.makeClusterGroups(this.country_code_list, this.index)
	//    console.log(this.index)
	var marker = L.marker([src[0], src[1]],{icon: this.makeCustomMarker()})
	var popup = L.Popup({
	    maxHeight: 50})
	var popupcontent = "<a href='https://en.wikipedia.org/wiki/"+this.country_code_list[this.index]+"' target='_blank'><img src='images/world/"+this.country_code_list[this.index]+".png'/></a>"
            +"<br />-------------<br />"        
            +"IP: <br /><a onclick='bcHistory.display_by_ip(\""+this.hn+"\",\""+this.index+"\")' href='#'>"
            +this.hop_ip_list[this.index]+"</a><br />"
	    +"Server name:<br /><a onclick='bcHistory.display_by_net(\""+this.hn+"\",\""+this.index+"\")' href='#'>"
	    +this.server_name_list[this.index]+"</a><br />"
            //+"Network owner:<br /><b>"+this.telco_list[this.index]+"</b><br />"
            +"Network owner:<br /><a onclick='bcHistory.displayMetadata(\""+this.hn+"\",\""+this.index+"\")' href='#'>"
            +this.telco_list[this.index]+"</a>"
            //+" IP: <b>"+this.hop_ip_list[index]+"</b>"
     
	marker.bindPopup(popupcontent)
	this.AddMarkerCluster(marker, this.index)
	this.drawnLayers.push(marker)
    }

    this.displayMetadata=function(index){
            duck_link= "";// parse when no network owner available for DuckGo
            wikileaks_link= "";// parse when no network owner available for wikileaks
            if (this.telco_list[index] == "Unknown"){
              duck_link =duck_link;
            }else{
              duck_link =duck_link+"<a target='_blank' href='https://duckduckgo.com/?q="+this.telco_list[index]+"'>DuckGo</a><br />"
            }
            if (this.telco_list[index] == "Unknown"){
              wikileaks_link =wikileaks_link;
            }else{
              wikileaks_link =wikileaks_link+"<a target='_blank' href='https://search.wikileaks.org/?q="+this.telco_list[index]+"'>Wikileaks</a>"
            }
	$(".bc-custom-control").html("<a href='#' onclick='$(\".bc-custom-control\").hide()'><img src=\"images/close.png\" style=\"float:right\"/></a><br />"
            +"Network owner:<br /><b>"+this.telco_list[index]+"</a></b>"
            +"<br />-------------<br />"
            // aded DuckGoDuck
            +duck_link
            // added Wikileaks
            +wikileaks_link)
	$(".bc-custom-control").show()
    }

    this.display_by_net=function(index){
            asn_link= '' // parse when no asn available
            if (this.asn_list[index] == "Not Available"){
              asn_link =asn_link+"?";
            }else{
              asn_link =asn_link+"<a target='_blank' href='https://www.ultratools.com/tools/asnInfoResult?domainName="+this.asn_list[index]+"'>"+this.asn_list[index]+"</a>"
            }
        $(".bc-custom-control").html("<a href='#' onclick='$(\".bc-custom-control\").hide()'><img src=\"images/close.png\" style=\"float:right\"/></a><br />"
            +"Server name:<br /><b>"+this.server_name_list[index]+"</b>"
            +"<br />-------------<br />"
            +"ASN: <b>"+asn_link+"</b><br />"
            +"Lat,Long: <b>"
            +this.latlong[index]+ "</b>")
        $(".bc-custom-control").show()
    }

    this.display_by_ip=function(index){
        $(".bc-custom-control").html("<a href='#' onclick='$(\".bc-custom-control\").hide()'><img src=\"images/close.png\" style=\"float:right\"/></a><br />"
            +"IP: <b>"+this.hop_ip_list[index]+"</b>"
            +"<br />-------------<br />"
            // added Who.is
            +"<a target='_blank' href='https://who.is/whois-ip/ip-address/"+this.hop_ip_list[index]+"'>Whois</a><br />"
            // added Shodan.io
            +"<a target='_blank' href='https://www.shodan.io/search?query="+this.hop_ip_list[index]+"'>ShodanHQ</a><br />"
            // added Wolfram
            +"<a target='_blank' href='http://www.wolframalpha.com/input/?i="+this.hop_ip_list[index]+"'>Wolfram</a>")
        $(".bc-custom-control").show()
    }
    
    this.addStep=function (){
	if(this.stop_anim){
//	    console.log(this.hn+" : addstep/stopping anim")
	    this.stop_anim=false
	    this.run_anim=false;
	    return
	}
//	console.log(this.hn+" : add step "+this.index)
	var src = this.latlong[this.index]
	var dest = this.latlong[this.index]
	if (this.index < this.counter_max){
	    var dest = this.latlong[this.index+1]
	}
	var b = new R.BezierAnim([src, dest])
	map.addLayer(b)
	this.drawnLayers.push(b)
	this.AddMarker(src, this.index)
	if (this.index < this.counter_max){
	    map.panTo(this.latlong[this.index+1],{
		animate: true,
		duration: this.speed/1000
	    })
        }
	else
	    if (this.index == this.counter_max){
		map.panTo(this.latlong[this.index],{
		    animate: true,
		    duration: this.speed/1000
		})
	    }
	window.setTimeout("bcHistory.process('"+this.hn+"')", this.speed)
    }
    
    this.processStep=function  () {
	if(this.stop_anim){
//	    console.log(this.hn+" : processstep/stopping anim")
	    this.stop_anim=false
	    this.run_anim=false;
	    return
	}
	console.log(this.hn+" : process step "+this.index)
	this.delay = (100 + this.timestamp_list[this.index])
	if (this.index < this.counter_max){
	    changeFavicon('images/world/'+this.country_code_list[this.index]+'.png')
	    window.setTimeout("bcHistory.addStep('"+this.hn+"')",this.delay)
	}
	if (this.index == this.counter_max){
	    //  map.panTo(latlong[this.index]);
	    changeFavicon('images/world/'+this.country_code_list[this.index]+'.png')
	    this.run_anim=false
	    this.state='show'
	    $("#status").html("Showing...")
//	    console.log('fin')
//	    map.fitBounds([bounds])
	}
	this.index = this.index + 1
    }

    this.stop=function(){
	if(this.index >0){
	    this.state='show'
	    $("#status").html("Showing...")
	}
	this.stop_anim=true
    }

    this.hide=function() {
//	console.log ("hiding "+  this.hn)
//	if(this.state=='show'){
	$('.header').hide()
	this.index =0
	    this.state='hidden'
	    this.stop_anim=true
	    for (i in this.drawnLayers){
//	    console.log("removing layer "+i)
//	    console.log(this.drawnLayers[i])
		if(map.hasLayer(this.drawnLayers[i]))
		    map.removeLayer(this.drawnLayers[i])
	    }
	    this.drawnLayers=new Array()
	}
//    }
}

function  bcHistoryClass(){
    this.cur_url="";
    this.last_url="";
    this.bcHistoryEntries = new Array

    this.find=function (hn){
	for (bcEntry in this.bcHistoryEntries){
	    if (this.bcHistoryEntries[bcEntry].hn === hn){
		return this.bcHistoryEntries[bcEntry]
	    }
	}
	return false;
    }

    this.process=function (hn){
	bce=this.find(hn)
	if(bce) bce.processStep()
    }

    this.addStep=function(hn){
	bce=this.find(hn)
	if(bce) bce.addStep()
    }
    
    this.render=function(){
	$("#history-content").html("");
	for (bcEntry in this.bcHistoryEntries){
//	    console.log(bcHistoryEntries[bcEntry]);
	    $("#history-content").append(this.bcHistoryEntries[bcEntry].makeLink())
	}
    }

    this.load=function(hn){
//	console.log("loadin "+hn);
	e=this.find(hn)
	if(e){
	    e.show()
	    return
	}
//	console.log("loadin "+hn+" failed !" );
	return false
    }

    this.play = function(hn){
	var bce=this.find(hn)
	if(!bce) return
	this.hideAll()
	bce.show()
	this.render()
    }

    this.hideAll = function(hn){
	for (bce in this.bcHistoryEntries)
	    this.bcHistoryEntries[bce].hide()
	this.render()
    }

    this.hide = function(hn){
	var bce=this.find(hn)
	if(!bce) return
	bce.hide()
	this.render()
    }

    this.displayMetadata = function(hn,index){
	var bce=this.find(hn)
	if(!bce) return
	return bce.displayMetadata(index);
    }

    this.display_by_net = function(hn,index){
        var bce=this.find(hn)
        if(!bce) return
        return bce.display_by_net(index);
    }

    this.display_by_ip = function(hn,index){
        var bce=this.find(hn)
        if(!bce) return
        return bce.display_by_ip(index);
    }

    this.remove = function(hn){
//	console.log("removing " + hn)
//	console.log(this.bcHistoryEntries)
	for (bcEntry in this.bcHistoryEntries){
	    if(this.bcHistoryEntries[bcEntry].hn === hn){
//		console.log("removing "+ this.bcHistoryEntries[bcEntry].hn +" | "+ hn)
		this.bcHistoryEntries[bcEntry].hide()
		this.bcHistoryEntries.splice(bcEntry,1)
		this.render()
		return
	    }
	}
    }

    this.add = function(hn,data){
//	console.log("adding " + hn)
	var bce=this.find(hn)
	if(!bce){
	    console.log("adding " + hn)
	    bce=new bcHistoryEntry(hn,data)
	    this.cur_url=hn
	    this.bcHistoryEntries.push(bce)
	    this.play(hn)
	}
	return bce
    }


    this.stop=function() {
	for(i=0;i<this.bcHistoryEntries.length;i++) {
	    this.bcHistoryEntries[i].stop();
	}  
	this.render()
    }
}

var bcHistory=new bcHistoryClass()
var cur_url=""
