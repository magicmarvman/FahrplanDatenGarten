from zipfile import ZipFile

from django.http import HttpResponse
from core import models
from django.core.cache import cache
import csv,io
# Create your views here.

def agencyexport():
    output = io.StringIO()

    fieldnames = ['agency_id', 'agency_name', 'agency_url', 'agency_timezone']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for agency in models.Agency.objects.all():
        writer.writerow({'agency_id': agency.id, 'agency_name': agency.name, 'agency_url': 'http://localhost', 'agency_timezone': 'Europe/Berlin'})
    return output.getvalue()

def stopexport():
    output = io.StringIO()

    fieldnames = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for stop in models.Stop.objects.all().prefetch_related("stopname_set","stoplocation_set"):
        stopname = stop.stopname_set.first()
        stoplocation = stop.stoplocation_set.first()
        if stoplocation:
            writer.writerow({'stop_id': stop.id, 'stop_name': stopname, 'stop_lat': stoplocation.latitude, 'stop_lon': stoplocation.longitude})
        else:
            writer.writerow({'stop_id': stop.id, 'stop_name': stopname})

    return output.getvalue()

def routesexport():
    output = io.StringIO()

    fieldnames = ['route_id', 'agency_id', 'route_short_name', 'route_type']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for journey in models.Journey.objects.all():
        if journey.name:
            writer.writerow({'route_id': journey.journey_id, 'agency_id': journey.agency.id, 'route_short_name': journey.name, 'route_type': 2})

    return output.getvalue()

def tripexport():
    output = io.StringIO()

    fieldnames = ['route_id', 'service_id', 'trip_id']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for journey in models.Journey.objects.all():
        if journey.name:
            writer.writerow({'route_id': journey.journey_id, 'service_id': journey.date, 'trip_id': journey.journey_id})

    return output.getvalue()

def stoptimesexport():
    output = io.StringIO()

    fieldnames = ['trip_id', 'arrival_time', 'departure_time','stop_id','stop_sequence']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for i,stoptimes in enumerate(models.JourneyStop.objects.all()):
        arrival_time = None
        if stoptimes.planned_arrival_time:
            arrival_time = (stoptimes.planned_arrival_time.date() - stoptimes.journey.first_date().date()).days * 24
            arrival_time = "{:02}:{:02}:{:02}".format(arrival_time, stoptimes.planned_arrival_time.hour, stoptimes.planned_arrival_time.minute)

        departure_time = None
        if stoptimes.planned_departure_time:
            departure_time = (stoptimes.planned_departure_time.date() - stoptimes.journey.first_date().date()).days * 24
            departure_time = "{:02}:{:02}:{:02}".format(departure_time, stoptimes.planned_departure_time.hour, stoptimes.planned_departure_time.minute)

        arrival_time = arrival_time or departure_time
        departure_time = departure_time or arrival_time

        writer.writerow({'trip_id': stoptimes.journey.journey_id, 'arrival_time': arrival_time, 'departure_time': departure_time,'stop_id': stoptimes.stop.id,'stop_sequence': i})

    return output.getvalue()

def calendardatesexport():
    output = io.StringIO()

    fieldnames = ['service_id', 'date', 'exception_type']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()
    services = set()
    for departure_date,arrival_date in models.JourneyStop.objects.all().values_list('planned_departure_time','planned_arrival_time'):
        if departure_date:
            services.add((departure_date.strftime("%Y-%m-%d"), departure_date.strftime("%Y%m%d")))
        if arrival_date:
            services.add((arrival_date.strftime("%Y-%m-%d"), arrival_date.strftime("%Y%m%d")))
    for i,d in services:
        writer.writerow({'service_id': i, 'date': d, 'exception_type': 1})
    return output.getvalue()

def gtfsexport(request):
    zipfile = io.BytesIO();
    with ZipFile(zipfile, 'w') as myzip:
        myzip.writestr("agency.txt",agencyexport())
        if not cache.get("stops.txt"):
            cache.set("stops.txt",stopexport(),24*60*60)
        myzip.writestr("stops.txt", cache.get("stops.txt"))
        myzip.writestr("routes.txt", routesexport())
        myzip.writestr("trips.txt", tripexport())
        myzip.writestr("stop_times.txt", stoptimesexport())
        myzip.writestr("calendar_dates.txt", calendardatesexport())
    return HttpResponse(zipfile.getvalue(),content_type="application/zip")
