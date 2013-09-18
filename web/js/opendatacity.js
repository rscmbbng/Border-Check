var DEFAULT_POINT = new L.LatLng(52.50085, 13.42232);
var map;
var rapath;
var info;

function RaPath() {
	this.layers = [];
	this.timeout = null;
}

RaPath.prototype = {
	addPathPart: function (hop_src, hop_dest, cb) {
		var b = new R.BezierAnim([hop_src.p, hop_dest.p], {}, function () {
			if (cb)
				cb();
		});
		this.layers.push(b);
		map.addLayer(b);
	},
	addPulse: function (hop) {
		var pulse = new R.Pulse(
			hop.p,
			3,
			{'stroke': '#2478ad', 'fill': '#30a3ec'},
			{'stroke': '#30a3ec', 'stroke-width': 2});
		pulse.tooltip = this.getHopsText(hop);
//		var caller = this;
		pulse.click = function (e) {
			//alert(caller.getHopsText(hop));
//			var popup = L.popup()
//				.setLatLng(hop.p)
//				.setContent(caller.getHopsText(hop))
//				.openOn(map);
		};
		this.layers.push(pulse);
		map.addLayer(pulse);
		return pulse;
	},
	getHopsText: function (hop) {
		return hop.ip + ' - ' + (hop.geo.city ? hop.geo.city + ', ' : '') + hop.geo.country;
	},
	clear: function () {
		if (this.timeout)
			window.clearTimeout(this.timeout);
		this.timeout = null;
		this.setButton(false);
		if (this.layers.length > 0)
			this.layers.forEach(function (l) {
				map.removeLayer(l);
			});
		info.clear();
	},
	setButton: function (active) {
		if (this.geotrace)
			if (active)
				$('#btn_' + this.geotrace.id).addClass('btn_active', active);
			else
				$('#btn_' + this.geotrace.id).removeClass('btn_active', active);
	},
	start: function (geotrace) {
		$('.leaflet-top').fadeIn();
		this.clear();
		this.geotrace = geotrace;
		this.layers = [];
		info.append(texts.requestline + ' ' + geotrace.name);
		this.setButton(true);
		this.processStep(0);
	},
	processStep: function (index) {
		var hop = this.geotrace.hops[index];
		info.append(this.getHopsText(hop));
		this.addPulse(hop);
		map.panTo(hop.p);
		var caller = this;
		this.timeout = window.setTimeout(function () {
			caller.stepPath(index + 1);
		}, 200);
	},
	displayEnd: function () {
		//this.setButton(false); just let it active
		//$('.leaflet-control-zoom').show();
		var result = [];
		for (key in this.geotrace.agencies) {
			result.push(this.geotrace.agencies[key].name + ' (' + this.geotrace.agencies[key].cc + ')');
		}
		info.append('<div id="agencies">' + texts.resultline + '</div>');
		info.append('<div id="agencies">' + result.join(' - ') + '</div>');
		map.fitBounds(this.geotrace.bounds);
	},
	stepPath: function (index) {
		var caller = this;
		if (index >= this.geotrace.hops.length) {
			this.timeout = window.setTimeout(function () {
				caller.displayEnd();
			}, 3000);
			return;
		}
		this.addPathPart(this.geotrace.hops[index - 1], this.geotrace.hops[index], function () {
			caller.processStep(index);
		});
	}
};

function getUrlVars() { // Read a page's GET URL variables and return them as an associative array.
	var vars = {},
		hash;
	var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
	for (var i = 0; i < hashes.length; i++) {
		hash = hashes[i].split('=');
		vars[hash[0]] = hash[1];
	}
	return vars;
}

function init() {
	try {
		var query = getUrlVars();
		if (query.src) {
			if (query.src == 'ch')
				selectSrc('ch');
			else
			if (query.src == 'fr')
				selectSrc('fr');
		}
		if ((query.colors) && (query.colors == "nzz")) {
			$('body').attr('colors', "nzz");
		}

	}
	catch (e) {
		//nop;
	}

	map = new L.Map("map", { center: DEFAULT_POINT, zoom: 3});

	map.addLayer(
		new L.TileLayer("http://trace.opendatacloud.de/{z}/{x}/{y}.png ",
			{attribution: 'OpenDataCity, CC-BY',
				minZoom: 2,
				maxZoom: 5}
		)
	);

	rapath = new RaPath();

	var legend = L.control({position: 'bottomleft'});
	legend.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'legend');
		$(div).html('<div class="legend border"><span id="cable">&nbsp</span> ' + texts.cable + '</div>');
		return div;
	};
	legend.addTo(map);

	info = L.control({position: 'topleft'});
	info.onAdd = function (map) {
		var div = L.DomUtil.create('div', 'hops');
		this._div = $(div);
		this._div.attr('id', 'hops');
		this._div.empty();
		if (isFrame) {
			this.append('<span class="upper">' + texts.tagline + '</span>');
			this.append(texts.subline);
			this.append(texts.helpline);
		}
		return div;
	};
	info.setText = function (txt) {
		this._div.text(txt);
	};
	info.setHTML = function (h) {
		this._div.html(h);
	};
	info.append = function (txt) {
		if (this._div.children().length > 30)
			this._div.children().first().remove();
		this._div.append('<p>' + txt + '</p>');

		this._div.scrollTop(this._div.prop("scrollHeight"));
	};
	info.clear = function () {
		this._div.empty();
	};
	info.addTo(map);


	//var lines = [texts.helpline];
	//new Typing().beginTyping(lines, $('#hops'));
}

function showRoute(id) {
	if (routedata[id]) {
		var route_agencies = {};
		var routes = routedata[id].routes;
		if (routes && routes.length) {
			var route = routes[(parseInt((Math.random() * 1000), 10) % routes.length)];
			var geotrace = {};
			geotrace.hops = [];
			for (var i = 0; i < route.trace.length; i++) {
				var ip = route.trace[i];
				var geo = geoinfo[ip];
				var hop = {
					p: new L.LatLng(geo.lat, geo.lng),
					ip: ip,
					geo: geo
				};
				var agency = agencies[geo.cc];
				if (agency)
					route_agencies[agency.name] = agency;
				geotrace.hops.push(hop);
			}
			var southWest = new L.LatLng(route.south, route.west),
				northEast = new L.LatLng(route.north, route.east);
			geotrace.bounds = new L.LatLngBounds(southWest, northEast);
			geotrace.agencies = route_agencies;
			geotrace.id = id;
			geotrace.name = routedata[id].name;
			rapath.start(geotrace);
		}
	}
}

function selectSrc(cc) {
	$('body').attr('requests', cc);
}

$(document).ready(function () {
	init();
});