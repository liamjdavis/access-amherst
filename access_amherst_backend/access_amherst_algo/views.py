from django.shortcuts import render, redirect
from .models import Event
from django.core.management import call_command
from django.db.models import Count
from django.db.models.functions import ExtractHour
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
import pytz
import re

# View to run db_saver command
def run_db_saver(request):
    call_command('db_saver')
    return redirect('../')

# View to run events_list_creator command
def run_events_list_creator(request):
    call_command('events_list_creator')
    return redirect('../')

# View to run json_saver command
def run_json_saver(request):
    call_command('json_saver')
    return redirect('../')

# View to run rss_fetcher command
def run_rss_fetcher(request):
    call_command('rss_fetcher')
    return redirect('../')

def run_hub_data_cleaner(request):
    call_command('hub_data_cleaner')
    return redirect('../')

# Home view with search functionality
def home(request):
    # Get query, location filter, start and end date from request
    query = request.GET.get('query', '')
    locations = request.GET.getlist('locations')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter events
    events = Event.objects.all()
    if query:
        events = events.filter(title__icontains=query)
    if locations:
        events = events.filter(location__in=locations)
    if start_date and end_date:
        events = events.filter(start_time__date__range=[start_date, end_date])

    # Remove duplicate events
    events = events.distinct()

    # Get unique locations for multiple-choice filter
    unique_locations = Event.objects.values_list('location', flat=True).distinct()

    # Pass context to template
    return render(request, 'access_amherst_algo/home.html', {
        'events': events,
        'query': query,
        'selected_locations': locations,
        'start_date': start_date,
        'end_date': end_date,
        'unique_locations': unique_locations
    })

def get_lat_lng(location):
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location_obj = geolocator.geocode(location)
        if location_obj:
            return location_obj.latitude, location_obj.longitude
    except:
        pass
    return None, None

def map_view(request):
    # Get events with titles and locations
    events = Event.objects.exclude(location__isnull=True).exclude(location__exact='')

    # Initialize Folium Map centered around Amherst College
    amherst_college_coords = [42.37031303771378, -72.51605520950432]
    folium_map = folium.Map(location=amherst_college_coords, zoom_start=18)

    # Add markers for events with latitude and longitude
    for event in events:
        if event.latitude is not None and event.longitude is not None:
            folium.Marker(
                location=[event.latitude, event.longitude],
                popup=f"<strong>{event.title}</strong><br>{event.location}",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(folium_map)

    # Generate the HTML representation of the map
    map_html = folium_map._repr_html_()

    # Pass the generated map HTML to the template
    return render(request, 'access_amherst_algo/map.html', {'map_html': map_html})

# View for data dashboard
def data_dashboard(request):
    # Set EST timezone
    est = pytz.timezone('America/New_York')

    # Group events by hour of the day and count them, converting start_time to EST
    events_by_hour = (
        Event.objects
        .annotate(hour=ExtractHour('start_time'))  # Extract UTC time first
        .values('hour')
        .annotate(event_count=Count('id'))
        .order_by('hour')
    )

    # Adjust the hours to EST
    for event in events_by_hour:
        start_time_utc = datetime.combine(datetime.now(), datetime.min.time()).replace(hour=event['hour'], tzinfo=pytz.utc)
        start_time_est = start_time_utc.astimezone(est)
        event['hour'] = start_time_est.hour

    # Count events by category
    events_by_category = []
    for event in Event.objects.exclude(categories__isnull=True).exclude(categories__exact=''):
        categories = event.categories.split(',')
        categories = [re.sub(r'[\"\[\]]', '', category) for category in categories]
        events_by_category.extend(categories)

    # Aggregate category counts
    category_counts = {}
    for category in events_by_category:
        category = category.strip().lower()
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1

    # Generate a Folium map with a heatmap layer for event density
    amherst_college_coords = [42.37031303771378, -72.51605520950432]
    folium_map = folium.Map(location=amherst_college_coords, zoom_start=14)

    # Create heatmap data from event locations
    heatmap_data = [
        [event.latitude, event.longitude]
        for event in Event.objects.exclude(latitude__isnull=True, longitude__isnull=True)
    ]

    # Add HeatMap layer to Folium map if data is available
    if heatmap_data:
        HeatMap(heatmap_data).add_to(folium_map)

    # Render the map as HTML
    map_html = folium_map._repr_html_()

    # Pass the data to the template
    context = {
        'events_by_hour': events_by_hour,
        'category_counts': category_counts,
        'map_html': map_html
    }
    return render(request, 'access_amherst_algo/dashboard.html', context)