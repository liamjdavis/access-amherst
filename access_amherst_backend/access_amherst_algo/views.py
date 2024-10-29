from django.shortcuts import render, redirect
from .models import Event
from django.core.management import call_command
from django.db.models import Count
from django.db.models.functions import ExtractHour
import datetime

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

def map_view(request):
    # Get events with titles and locations
    events = Event.objects.exclude(location__isnull=True).exclude(location__exact='')
    event_data = [
        {
            "title": event.title,
            "location": event.location  # Assuming this is the location name
        }
        for event in events
    ]
    return render(request, 'access_amherst_algo/map.html', {'event_data': event_data})

# View for data dashboard
def data_dashboard(request):
    # Group events by hour of the day and count them
    events_by_hour = (
        Event.objects
        .annotate(hour=ExtractHour('start_time'))  # Use ExtractHour for cross-database compatibility
        .values('hour')
        .annotate(event_count=Count('id'))
        .order_by('hour')
    )

    # Count events by category (assuming categories are stored as comma-separated strings)
    events_by_category = []
    for event in Event.objects.exclude(categories__isnull=True).exclude(categories__exact=''):
        categories = event.categories.split(',')
        events_by_category.extend(categories)
    
    # Aggregate category counts
    category_counts = {}
    for category in events_by_category:
        category = category.strip().lower()  # Normalize
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1

    # Pass the data to the template
    context = {
        'events_by_hour': events_by_hour,
        'category_counts': category_counts
    }
    return render(request, 'access_amherst_algo/dashboard.html', context)