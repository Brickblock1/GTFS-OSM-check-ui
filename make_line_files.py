import csv, json, argparse, os

parser = argparse.ArgumentParser()
parser.add_argument("code", help="The prefix of the folder the generetad files will be dumped to in the data folder.")
args = parser.parse_args()

code = args.code

feedinfo = open(f"gtfs/feed_info.txt", "r", encoding="UTF8")
feedinfo = list(csv.reader(feedinfo))

version = feedinfo[1][feedinfo[0].index("feed_version")]

def list_to_dict(headers, list):
    return_dict = dict()
    for i in range(len(list)):
        return_dict[headers[i]] = list[i]
    return return_dict

routes_dict = dict()
trips_dict = dict()
stops_dict = dict()
stop_refs_dict = dict()
calendar_dict = dict()

#special
shape_trips_dict = dict()

routes = open(f"gtfs/routes.txt", "r", encoding="UTF8")
routes = csv.reader(routes)
routes = list(routes)
route_headers = list()
for route in routes:
        if route is routes[0]:
            for header in route:
                route_headers.append(header)
        else:
            routes_dict[route[0]] = list_to_dict(route_headers, route)

trips = open(f"gtfs/trips.txt", "r", encoding="UTF8")
trips = csv.reader(trips)
trips = list(trips)
trip_headers = list()
prev_trip_shape = set()
for trip in trips:
    # spacial handeling of first line
    if trip is trips[0]:
        for header in trip:
            trip_headers.append(header)
    else:
        if trip[0]+trip[5] in prev_trip_shape:
            shape_trips_dict[trip[0]+trip[5]].append({trip_headers[2]: trip[2], trip_headers[1]: trip[1]})
        else:
            shape_trips_dict[trip[0]+trip[5]] = list()
            shape_trips_dict[trip[0]+trip[5]].append({trip_headers[2]: trip[2], trip_headers[1]: trip[1]})
            prev_trip_shape.add(trip[0]+trip[5])

prev_trip = set()
for trip in trips:
    # spacial handeling of first line
    if trip is not trips[0]:
        if trip[0] in prev_trip:
            trips_dict[trip[0]][trip[5]] = dict(shape_id = trip[5], trips = shape_trips_dict[trip[0]+trip[5]])
        else:
            trips_dict[trip[0]] = dict()
            trips_dict[trip[0]][trip[5]] = dict(shape_id = trip[5], trips = shape_trips_dict[trip[0]+trip[5]])
            prev_trip.add(trip[0])


def get_shapes(code):
    shapes_dict = dict()
    shapes = open(f"gtfs/shapes.txt", "r", encoding="UTF8")
    shapes = csv.reader(shapes)
    shapes = list(shapes)
    shape_headers = list()
    prev_shape = None
    for shape in shapes:
        if shape is shapes[0]:
            for header in shape:
                shape_headers.append(header)
        else:
            if shape[0] == prev_shape:
                shapes_dict[shape[0]].append([shape[1], shape[2]])
            else:
                shapes_dict[shape[0]] = list()
                shapes_dict[shape[0]].append([shape[1], shape[2]])
                prev_shape = shape[0]

    return shapes_dict

stops = open(f"gtfs/stops.txt", "r", encoding="UTF8")
stops = csv.reader(stops)
stops = list(stops)
stop_headers = list()
for stop in stops:
    if stop is stops[0]:
        for header in stop:
            stop_headers.append(header)
    else:
        stops_dict[stop[0]] = list_to_dict(stop_headers, stop)

stop_refs = open(f"gtfs/stop_times.txt", "r", encoding="UTF8")
stop_refs = csv.reader(stop_refs)
stop_refs = list(stop_refs)
stop_ref_headers = list()
prev_stop_ref = None
for stop_ref in stop_refs:
    if stop_ref is stop_refs[0]:
        for header in stop_ref:
            stop_ref_headers.append(header)
    else:
        if stop_ref[0] == prev_stop_ref:
            stop_refs_dict[stop_ref[0]].append({stop_ref[3]: {stop_ref_headers[6]: stop_ref[6], stop_ref_headers[7]: stop_ref[7], stop_ref_headers[3]: stop_ref[3]}})
        else:
            stop_refs_dict[stop_ref[0]] = list()
            stop_refs_dict[stop_ref[0]].append({stop_ref[3]: {stop_ref_headers[6]: stop_ref[6], stop_ref_headers[7]: stop_ref[7], stop_ref_headers[3]: stop_ref[3]}})
            prev_stop_ref = stop_ref[0]

shapes_dict = get_shapes(code)

calendar = open(f"gtfs/calendar.txt", "r", encoding="UTF8")
calendar = csv.reader(calendar)
calendar = list(calendar)
calendar_headers = list()
for row in calendar:
    if row is calendar[0]:
        for header in row:
            calendar_headers.append(header)
    else:
        calendar_dict[row[0]] = {calendar_headers[0]: row[0], calendar_headers[8]: row[8], calendar_headers[9]: row[9]}

#for debugging 

#export = open(f"routes_dict.json", 'w', encoding="UTF8")
#json.dump(routes_dict, export, indent=2)
#export = open(f"trips_dict.json", 'w', encoding="UTF8")
#json.dump(trips_dict, export, indent=2)
#export = open(f"shapes_dict.json", 'w', encoding="UTF8")
#json.dump(shapes_dict, export, indent=2)
#export = open(f"stops_dict.json", 'w', encoding="UTF8")
#json.dump(stops_dict, export, indent=2)
#export = open(f"stop_refs_dict.json", 'w', encoding="UTF8")
#json.dump(stop_refs_dict, export, indent=2)
#export = open(f"calendat_dict.json", 'w', encoding="UTF8")
#json.dump(calendar_dict, export, indent=2)


# Write route specific files THIS CODE IS CURSED TRY TO AVOID IT
try:
    os.mkdir(f"./data/{code}")
except:
    print(f"./data/{code} directory will be overriden.")

for route in routes_dict.values():
    route_dict = dict()
    route_dict["feed_version"] = version
    route_dict.update(route)
    route_dict["shapes"] = list(trips_dict[route["route_id"]].values())
    for shape in range(len(route_dict["shapes"])):
        route_dict["shapes"][shape]["points"] = shapes_dict[route_dict["shapes"][shape]["shape_id"]]
        for trip in range(len(route_dict["shapes"][shape]["trips"])):
            route_dict["shapes"][shape]["trips"][trip]["stops"] = stop_refs_dict[route_dict["shapes"][shape]["trips"][trip]["trip_id"]]
            route_dict["shapes"][shape]["trips"][trip]["service"] = calendar_dict[route_dict["shapes"][shape]["trips"][trip]["service_id"]]
            for stop in range(len(route_dict["shapes"][shape]["trips"][trip]["stops"])):
                    route_dict["shapes"][shape]["trips"][trip]["stops"][stop] = list(stop_refs_dict[route_dict["shapes"][shape]["trips"][trip]["trip_id"]][stop].values())[0]
                    route_dict["shapes"][shape]["trips"][trip]["stops"][stop].update(stops_dict[list(route_dict["shapes"][shape]["trips"][trip]["stops"][stop].values())[2]])
                
    export = open(f"data/{code}/route_{route['route_id']}.json", 'w', encoding="UTF8")
    json.dump(route_dict, export, indent=2)

export = open(f"data/{code}/routes.json", 'w', encoding="UTF8")
json.dump(routes_dict, export, indent=2)

clean_stops_dict = {}

inuse_stops = set()

for stopidk in stop_refs_dict.values():
    for stopidk2 in stopidk:
        #print(list(stopidk2.values()))
        #stopidk2 = list(stopidk2.values())[0]
        inuse_stops.add(stopidk2["stop_id"])

for stop in stops_dict.values():
    if stop["stop_id"] in inuse_stops:
        stop["inuse"] = True
    else:
        stop["inuse"] = False
    clean_stops_dict[stop["stop_id"]] = stop

export = open(f"data/{code}/stops.json", 'w', encoding="UTF8")
json.dump(clean_stops_dict, export, indent=2)

print("done")
