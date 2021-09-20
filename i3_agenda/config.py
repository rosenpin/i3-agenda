import os
from os.path import expanduser
import argparse

CONF_DIR = expanduser("~") + os.path.sep + ".i3agenda"
URL_REGEX = "(((http|https)://)?[a-zA-Z0-9./?:@\\-_=#]+\\.([a-zA-Z]){2,6}([a-zA-Z0-9.&/?:@\\-_=#])*)"


# i3blocks use this envvar to check the click
button = os.getenv("BLOCK_BUTTON", "")


parser = argparse.ArgumentParser(description="Show next Google Calendar event")
parser.add_argument(
    "--credentials",
    "-c",
    type=str,
    default="",
    help="path to your credentials.json file",
)
parser.add_argument(
    "--conf",
    "-cd",
    type=str,
    default=CONF_DIR,
    help="path to the i3agenda configuration and cache folder",
)
parser.add_argument(
    "--cachettl",
    "-ttl",
    type=int,
    default=30,
    help="time for cache to be kept in minutes",
)
parser.add_argument(
    "--update",
    "-u",
    action="store_true",
    default=False,
    help="""when using this flag it will not load previous results from cache, it will however save 
            new results to cache. You can use this flag to refresh all the cache forcefully""",
)
parser.add_argument(
    "--ids",
    "-i",
    type=str,
    default=[],
    nargs="+",
    help="list of calendar ids to fetch, space separated. If none is specified all calendars will be fetched",
)
parser.add_argument(
    "--maxres",
    "-r",
    type=int,
    default=10,
    help="""max number of events to query Google's API for each of your calendars. Increase this number if you 
            have lot of events in your google calendar""",
)
parser.add_argument(
    "--today", "-d", action="store_true", help="print only today events"
)
parser.add_argument(
    "--no-event-text",
    default="No events",
    metavar="TEXT",
    help="text to display when there are no events",
)
parser.add_argument(
    "--hide-event-after",
    type=int,
    default=-1,
    help="""minutes to show events after they start before showing the next event. If not specified, the current event
            will be shown until it ends""",
)
parser.add_argument(
    "--date-format",
    type=str,
    default="%d/%m",
    help="the date format like %%d/%%m/%%y. Default is %%d/%%m",
)
parser.add_argument(
    "--limchar",
    "-l",
    type=int,
    default=-1,
    help="the max characters that the displayed event can contain",
)
parser.add_argument(
    "--skip",
    "-s",
    type=int,
    default=0,
    help="the number of events to skip from the most recent",
)
