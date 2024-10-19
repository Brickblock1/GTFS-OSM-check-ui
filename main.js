function handle_stop(member, thing) {
  if (member.role.includes("platform")) {
    colour = "green";
  } else {
    colour = "red";
  }

  // Place a marker if node

  if (member.type == "node") {
    if (member.role.includes("platform")) {
      var stop = L.marker([member.lat, member.lon], {
        icon: greenDot,
      }).addTo(map);
    } else {
      var stop = L.marker([member.lat, member.lon], {
        icon: redDot,
      }).addTo(map);
    }

    // Place line if way // Add better support for areas
  } else if (member.type == "way") {
    let latlngs = [];
    for (let p of member.geometry) {
      latlngs.push([p.lat, p.lon]);
    }
    for (let global_entry of thing.elements) {
      if (global_entry.id == member.ref) {
        if (global_entry.tags.area == "yes") {
          var stop = L.polygon(latlngs, {
            color: colour,
          }).addTo(map);
        } else {
          var stop = L.polyline(latlngs, {
            color: colour,
          }).addTo(map);
        }
      }
    }

    // Place polygon if multipolygon after ways have been merged into an array of points
  } else if (member.type == "relation") {
    for (let global_entry of thing.elements) {
      if (global_entry.id == member.ref) {
        let latlngs = [];
        let un_latlngs = [];
        for (let global_multipolygon_way of global_entry.members) {
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
        var stop = L.polygon(latlngs, { color: colour }).addTo(map);
      }
    }
  }

  //Make popup for platform

  for (let global_entry of thing.elements) {
    if (global_entry.id == member.ref) {
      if (global_entry.tags.name == null) {
        stop_name = "Name not in OSM";
      } else {
        stop_name = global_entry.tags.name
      }
      stop.bindTooltip(`${stop_name} (${global_entry.tags["gtfs:platform_code:SE-003-UL"]})`);
      popup_text = ""
      for (entry of Object.entries(global_entry.tags)) {
        if (!(entry[0] == "stop_lon" || entry[0] == "stop_lat")) {
          popup_text = popup_text + entry[0] + "=" + entry[1] + "<br>"
        }
      }
      stop.bindPopup(popup_text)
    }
  }
}
