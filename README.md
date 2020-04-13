# Setup
1. You need to create a Google API application and download your OAuth 2.0 credentials json file to the same directory from which you will run the script  
You can do that here [https://developers.google.com/calendar/auth](https://developers.google.com/calendar/auth)
2. Run the script, it will print your next event
3. Add configuration to your bar

Example polybar configuration  
```
modules-center = agenda
....
[module/agenda]
type = custom/script
exec = cd ~/i3-agenda/ && python i3-agenda.py
click-left = chromium https://calendar.google.com/calendar/r/day
interval = 60
```

