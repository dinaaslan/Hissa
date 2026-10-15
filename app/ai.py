#Ai helper: reads the family sentences and finds the right match 
import re
DAYS={
    "saturday":"Sat",
    "sunday":"Sun",
    "monday":"Mon",
    "tuesday":"Tue",
    "wednesday":"Wed",
    "thursday":"Thu",
    "friday":"Fri",
}

def understand_need(sentence, subjects):
    text=sentence.lower()
    need={"subject":"", "days":[], "after":None, "at":None}
    #check if subject is one of the tutors subjects 
    for subject in subjects:
        if subject.lower() in text:
            need["subject"] =subject
    #check the day
    for word in DAYS:
        if word in text:
            need["days"].append(DAYS[word])
    if "weekend" in text:
        for day in["Fri", "Sat"]:
            if day not in need["days"]:
                need["days"].append(day)
    #check the time (after a certain time (PM))
    found=re.search(r"after (\d+)", text)
    if found:
        hour=int(found.group(1))
        if hour <8: 
            hour=hour+12
        need["after"] = hour
    found=re.search(r"\bat (\d+)", text)
    if found:
            hour=int(found.group(1))
            if hour <8: 
                hour=hour+12
            need["at"] = hour
    return need