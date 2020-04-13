# Setup
1. You need to create a Google API project and download your OAuth 2.0 credentials json file to the same directory from which you will run the script  
You can create your credentials here [https://console.developers.google.com/apis/credentials](https://console.developers.google.com/apis/credentials)  
If your'e having trouble, you can use this tutorial [https://developers.google.com/calendar/auth](https://developers.google.com/calendar/auth)  
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

Example output of the script:  
```11:00 Grocery shopping```

![example](art/screenshot.png)
