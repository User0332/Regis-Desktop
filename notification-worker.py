from notifypy import Notify
import time

while 1:
	Notify(
		"10 Seconds Have Passed",
		"This is a 10-second notification from Regis Desktop!",
		"Regis Desktop",
		default_notification_icon="assets/regis-icon.ico"
	).send()
	time.sleep(10)