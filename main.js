function openstreetmaps(type, id) {
  window.open("https://openstreetmaps.org/" + type + "/" + id, "_blank");
}

function handle_stop(stop, layer, stop_order, role) {
  if (role.includes("platform")) {
    colour = "green";
  } else {
    colour = "red";
  }

  // Place a marker if node

  if (stop.type == "node") {
    var map_stop = L.circle([stop.lat, stop.lon], {
      color: colour,
      fillColor: "grey",
      fillOpacity: 1,
      weight: 4,
      radius: 1,
    }).addTo(layer);

    // Place line if way // Add better support for areas
  } else if (stop.type == "way") {
    let latlngs = [];
    for (let p of stop.geometry) {
      latlngs.push([p.lat, p.lon]);
    }
    if (stop.tags.area == "yes") {
      var map_stop = L.polygon(latlngs, {
        color: colour,
      }).addTo(layer);
    } else {
      var map_stop = L.polyline(latlngs, {
        color: colour,
      }).addTo(layer);
    }
  }

  // Place polygon if multipolygon after ways have been merged into an array of points
  else if (stop.type == "relation") {
    let latlngs = [];
    for (let global_multipolygon_way of stop.members) {
      for (let i in global_multipolygon_way.geometry) {
        p = global_multipolygon_way.geometry[i];
        p2 = global_multipolygon_way.geometry.at(length - i);
        if (
          [
            global_multipolygon_way.geometry[i].lat,
            global_multipolygon_way.geometry[i].lon,
          ] == latlngs.at(-1) ||
          latlngs.length == 0
        ) {
          latlngs.push([p.lat, p.lon]);
        } else {
          latlngs.push([p.lat, p.lon]);
        }
      }
    }
    var map_stop = L.polygon(latlngs, { color: colour }).addTo(layer);
  }

  //Make popup for platform

  if (stop.tags != null) {
    if (stop.tags.name == null) {
      stop_name = "Name not in OSM";
    } else {
      stop_name = stop.tags.name;
    }
    map_stop.bindTooltip(`${stop_name} (${stop_order})`);
    popup_text = `<input type="button" value="Open at openstreetmaps.org" onclick="openstreetmaps('${stop.type}', '${stop.id}')"><br>`;
    for (entry of Object.entries(stop.tags)) {
      if (!(entry[0] == "stop_lon" || entry[0] == "stop_lat")) {
        popup_text = popup_text + entry[0] + "=" + entry[1] + "<br>";
      }
    }
    map_stop.bindPopup(popup_text);
  }
}
