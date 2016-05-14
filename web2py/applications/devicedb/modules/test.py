from datetime import datetime
from bulletin import process_trigger

d=datetime(2014,5,20,12,30)
print d
print d.weekday()


print process_trigger("time=12:30",d) == True
print process_trigger("time=12:31",d) == False
print process_trigger("weekday=Sunday",d) == False
print process_trigger("weekday=Monday",d) == True
print process_trigger("time=12:30 weekday=Monday",d) == True
print process_trigger("time=12:30 weekday=Sunday",d) == False
print process_trigger("time=12:31 weekday=Monday",d) == False
print process_trigger("time=12:31 weekday=Sunday",d) == False
print process_trigger("date=5-20",d) == True
print process_trigger("date=2014-5-20",d) == True
print process_trigger("date=2014-6-20",d) == False
print process_trigger("",d) == False




