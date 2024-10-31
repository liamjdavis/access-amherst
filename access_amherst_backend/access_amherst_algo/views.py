from django.shortcuts import render, redirect
from .models import Event
from django.core.management import call_command
from django.db.models import Count
from django.db.models.functions import ExtractHour
from datetime import datetime
import folium
from folium.plugins import HeatMap
import pytz

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
        events = events.filter(map_location__in=locations)
    if start_date and end_date:
        events = events.filter(start_time__date__range=[start_date, end_date])

    # Remove duplicate events
    events = events.distinct()

    # Get unique map locations for filtering
    unique_locations = Event.objects.values_list('map_location', flat=True).distinct()

    # Pass context to template
    return render(request, 'access_amherst_algo/home.html', {
        'events': events,
        'query': query,
        'selected_locations': locations,
        'start_date': start_date,
        'end_date': end_date,
        'unique_locations': unique_locations
    })

def map_view(request):
    # Fetch events with valid latitude and longitude
    events = Event.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    # Initialize map centered around Amherst College
    amherst_college_coords = [42.37031303771378, -72.51605520950432]
    folium_map = folium.Map(location=amherst_college_coords, zoom_start=18)

    # Add markers for each event using both latitude and longitude fields
    for event in events:
        folium.Marker(
            location=[float(event.latitude), float(event.longitude)],
            popup=f"<strong>{event.title}</strong><br>{event.location} ({event.map_location})",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(folium_map)

    # Render map as HTML
    map_html = folium_map._repr_html_()
    return render(request, 'access_amherst_algo/map.html', {'map_html': map_html})


# Dashboard view for data insights
def data_dashboard(request):
    # Set EST timezone
    est = pytz.timezone('America/New_York')

    # get events
    events = Event.objects.all()

    # Group events by hour of the day and count them
    events_by_hour = (
        Event.objects
        .annotate(hour=ExtractHour('start_time'))  # Extract UTC time
        .values('hour')
        .annotate(event_count=Count('id'))
        .order_by('hour')
    )

    # Convert event hours to EST
    for event in events_by_hour:
        start_time_utc = datetime.combine(datetime.now(), datetime.min.time()).replace(hour=event['hour'], tzinfo=pytz.utc)
        start_time_est = start_time_utc.astimezone(est)
        event['hour'] = start_time_est.hour

    # Count events by category
    events_by_category = Event.objects.exclude(categories__isnull=True).exclude(categories__exact='').values_list('categories', flat=True)
    category_counts = {}
    for categories in events_by_category:
        for category in categories.strip("[]\"").split(","):
            category = category.strip().lower()
            category_counts[category] = category_counts.get(category, 0) + 1

    # Generate a Folium map with a heatmap layer
    folium_map = folium.Map(location=[42.37031303771378, -72.51605520950432], zoom_start=14)
    heatmap_data = [[float(event.latitude), float(event.longitude)] for event in events if event.latitude and event.longitude]
    
    # Add HeatMap layer if data is available
    if heatmap_data:
        HeatMap(heatmap_data).add_to(folium_map)

    # Render map as HTML
    map_html = folium_map._repr_html_()

    # Pass the data to the template
    context = {
        'events_by_hour': events_by_hour,
        'category_counts': category_counts,
        'map_html': map_html
    }
    return render(request, 'access_amherst_algo/dashboard.html', context)