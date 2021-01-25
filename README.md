[![AUR version](https://img.shields.io/aur/version/i3-agenda?style=flat-square&logo=arch-linux)](https://aur.archlinux.org/packages/i3-agenda/)
[![PyPI](https://img.shields.io/pypi/v/i3-agenda?style=flat-square&logo=python)](https://pypi.org/project/i3-agenda/)


# What is this?
It's a script that communicates with Google's calendar API, it will go through your calendars and print the next calendar event details.\
You can take this output and show it on your i3-bar or polybar

![example](https://raw.githubusercontent.com/rosenpin/i3-agenda/master/art/screenshot.png)

## How does it work
It will read your next 10 events from each of your calendars, then go through them all and figure out which one is closest.\
It will print the time and title of the closest event.

# Setup

## Google API
https://developers.google.com/calendar/quickstart/python

1. You need to create a Google API project and download your OAuth 2.0 credentials json file.\
You first need to create a project [here](https://console.developers.google.com/apis/credentials), then add Google Calendar support, then download the credentials.json file.\
**Alternatively, you can just use [this link](https://developers.google.com/calendar/quickstart/python) and click "Enable the Google Calendar API". This will create a project, add Google Calendar support, and let you download the file in 1 click**.\
If you're having trouble, you can use this tutorial for more information [https://developers.google.com/calendar/auth](https://developers.google.com/calendar/auth).\
Another great guide can be found here if you're still having trouble: [https://github.com/jay0lee/GAM/wiki/CreatingClientSecretsFile](https://github.com/jay0lee/GAM/wiki/CreatingClientSecretsFile).
2. Download the credentials file to somewhere on your computer.
3. Proceed to installation phase.

## Installation
After downloading the credentials file, install the package.

### Pip
1. `sudo pip install i3-agenda`
2. Try running `i3-agenda -c $CREDENTIALS_FILE_PATH` with "$CREDENTIALS_FILE_PATH" replaced with the path to the credentials.json file you downloaded in the previous step.
3. Add configuration to your bar (examples in the Examples section below).

### Arch Linux (AUR)
1. `yay -S i3-agenda-git`
2. Try running `i3-agenda -c $CREDENTIALS_FILE_PATH` with "$CREDENTIALS_FILE_PATH" replaced with the path to the credentials.json file you downloaded in the previous step.
3. Add configuration to your bar (examples in the Examples section below).

### Manual
#### Dependencies
You need to install some python libraries first.\
Make sure python3 is your default python.\
Run `sudo pip3 install python-bidi google-api-python-client google-auth-httplib2 google-auth-oauthlib`

1. Clone the repo to a local directory `cd ~/ && git clone https://github.com/rosenpin/i3-agenda && cd i3-agenda`
3. Run the script `python3 i3_agenda/__init__.py -c $CREDENTIALS_FILE_PATH` with "$CREDENTIALS_FILE_PATH" replaced with the path to the credentials.json file you downloaded in the previous step. If configured correctly, it will prompt you to log in in your browser, accept everything. It should print your next event.
4. Optional: you can run `sudo python setup.py install` to add the script to your path so you can run `i3-agenda` anywhere.
5. Add configuration to your bar (examples in the Examples section below).

# Usage
```
  -h, --help            show this help message and exit
  --credentials CREDENTIALS, -c CREDENTIALS
                        path to your credentials.json file
  --cachettl CACHETTL, -ttl CACHETTL
                        time for cache to be kept in minutes
  --update, -u          when using this flag it will not load previous results from cache, it will however save new results to cache. You can use this flag to refresh all the cache forcefully
  --ids IDS [IDS ...], -i IDS [IDS ...]
                        list of calendar ids to fetch, space separated. If none is specified all calendars will be fetched
  --maxres MAXRES, -r MAXRES
                        max number of events to query Google's API for each of your calendars. Increase this number if you have lot of events in your google calendar
  --today, -d           print only today events
  --no-event-text TEXT  text to display when there are no events
  --hide-event-after MINUTES
                        minutes to show events after they start before showing the next event. If not specified, the current event will be shown until it ends
  --date-format DATEFORMAT
                        the date format like %d/%m/%y. Default is %d/%m
```

### Filter displayed calendars
To display events only from certain calendars use the `--ids` parameter and pass a list of calendar id, space separated.\
To obtain the calendar id you can check the settings page of the calendar on Google (usually is the owner email, if it's not shared).\
Leaving the list empty will fetch all calendars (default behavior).

## Notes
### Known issues
It might not work properly if you have more than 10 all day events, this can be fixed by increasing the maxResults variable.

### Caching
It uses a caching mechanism so you won't have to contact Google servers every minute, to set the cache TTL use the -ttl flag.\
Example: `i3-agenda --ttl 60` to set the TTL to 60 (meaning it will contact Google again every hour).\
This means that if you create a new event, it might take an hour for the script to recognize it.

## Examples
Example polybar configuration:
``` ini
modules-center = agenda
....
[module/agenda]
type = custom/script
; Show the next event and forget cache automatically every 60 minutes
exec = i3-agenda -c ~/.google_credentials.json -ttl 60
; left click to launch Google Calendar
click-left = chromium https://calendar.google.com/calendar/r/day
; right click force update the cache, if for example you just added a new event
click-right = notify-send "syncing..." && i3-agenda -c ~/.google_credentials.json --update && notify-send -t 2000 "sync finished"
interval = 60
```

Example i3block configuration:
```
[i3-agenda]
command=i3-agenda -c ~/.google_credentials.json -ttl 60
interval=60
```


Example output of the script:\
```10:55 Grocery shopping```
