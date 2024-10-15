from django.core.management.base import BaseCommand
from access_amherst_algo.rss_scraper.parse_rss import parse_rss

class Command(BaseCommand):
    help = 'Parses the RSS feed from the Amherst Hub'

    def handle(self, *args, **kwargs):
        parse_rss()
        self.stdout.write(self.style.SUCCESS('Successfully parsed the RSS feed from the Amherst Hub'))