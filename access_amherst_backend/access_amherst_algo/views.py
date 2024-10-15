# views.py
from django.shortcuts import render, redirect
from .models import Event
from django.core.management import call_command

# View to run db_saver command
def run_db_saver(request):
    call_command('db_saver')
    return redirect('access_amherst_algo/home.html')

# View to run events_list_creator command
def run_events_list_creator(request):
    call_command('events_list_creator')
    return redirect('access_amherst_algo/home.html')

# View to run json_saver command
def run_json_saver(request):
    call_command('json_saver')
    return redirect('access_amherst_algo/home.html')

# View to run rss_fetcher command
def run_rss_fetcher(request):
    call_command('rss_fetcher')
    return redirect('access_amherst_algo/home.html')

def home(request):
    # Fetch all events
    events = Event.objects.all()

    # Pass the events to the template context
    return render(request, 'access_amherst_algo/home.html', {'events': events})
