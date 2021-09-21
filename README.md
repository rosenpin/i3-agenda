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
  --conf CONF, -cd CONF
                        path to the i3agenda configuration and cache folder
  --cachettl CACHETTL, -ttl CACHETTL
                        time for cache to be kept in minutes
  --update, -u          when using this flag it will not load previous results from cache, it will however save new results to cache.
                        You can use this flag to refresh all the cache forcefully
  --ids IDS [IDS ...], -i IDS [IDS ...]
                        list of calendar ids to fetch, space separated. If  none is specified all calendars will be fetched
  --maxres MAXRES, -r MAXRES
                        max number of events to query Google's API for each of your calendars.
                        Increase this number if you have lot of events in your google calendar
  --today, -d           print only today events
  --no-event-text TEXT  text to display when there are no events
  --hide-event-after HIDE_EVENT_AFTER
                        minutes to show events after they start before showing the next event.
                        If not specified, the current event will be shown until it ends
  --date-format DATE_FORMAT
                        the date format like %d/%m/%y. Default is %d/%m
  --limchar LIMCHAR, -l LIMCHAR
                        the max characters that the displayed event can contain
  --skip SKIP, -s SKIP  the number of events to skip from the most recent
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

### Multi account support
Multi account support is not officialy supported, but you can use the workaround from this issue: https://github.com/rosenpin/i3-agenda/issues/35#issuecomment-923976482

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
```ini
[i3-agenda]
command=i3-agenda -c ~/.google_credentials.json -ttl 60
interval=60
```


Example output of the script:\
```10:55 Grocery shopping```

### How to use the `skip` flag to scroll events

Edit the polybar configuration creating two modules:

```ini
[module/agenda-ipc]
type = custom/ipc

hook-0 = i3-agenda -c ~/.google_credentials.json --skip $(cat ~/.config/i3-agenda/i3-agenda-skip.tmp || echo 0)
hook-1 = ~/.config/polybar/scripts/i3agenda-onscroll.sh down && i3-agenda -c ~/.google_credentials.json --skip $(cat ~/.config/i3-agenda/i3-agenda-skip.tmp || echo 0)
hook-2 = ~/.config/polybar/scripts/i3agenda-onscroll.sh up && i3-agenda -c ~/.google_credentials.json --skip $(cat ~/.config/i3-agenda/i3-agenda-skip.tmp || echo 0)

format = %{F#61afef}%{F-} <output>

; left click to launch Google Calendar
click-left = firefox https://calendar.google.com/calendar/u/0/r
; right click force update the cache, if for example you just added a new event
click-right = rm ~/.config/i3-agenda/i3-agenda-skip.tmp; i3-agenda -c ~/.config/i3-agenda/client_secret.json --update && notify-send "i3-agenda" "Sync completed"

; show the previous event
scroll-down = polybar-msg hook agenda-ipc 2
; show the next event
scroll-up = polybar-msg hook agenda-ipc 3

[module/agenda]
type = custom/script
interval = 900
exec = polybar-msg hook agenda-ipc 1
label =
```

Add both modules to the bar, for example:

```ini
modules-center = agenda agenda-ipc
```

In the polybar scripts folder add the file `i3agenda-onscroll.sh`:

```bash
#!/usr/bin/env bash
if [ -n "${1}" ]; then
  file=~/.config/i3-agenda/i3-agenda-skip.tmp
  typeset -i skip=$(cat $file || echo 0)
  if [[ "${1}" == "up" ]]; then
    skip+=1
  elif [[ "${1}" == "down" && $skip -gt 0 ]]; then
    skip=$(( skip - 1))
  fi
  echo $skip > $file
fi
```
