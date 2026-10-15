#Ai helper: reads the family sentences and finds the right match 
import re
import os #this reads the key
import json #json converts between text and dictionaries 
import urllib.request #this sends the request to Gemini
import urllib.error
DAYS={
    "saturday":"Sat",
    "sunday":"Sun",
    "monday":"Mon",
    "tuesday":"Tue",
    "wednesday":"Wed",
    "thursday":"Thu",
    "friday":"Fri",
}

#KEYWORD VERSION
def keyword_helper(sentence, subjects):
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

#GEMINI VERSION: ASKING THE AI TO READ THE SENTNENCE 
def gemini_helper(sentence, subjects):
    #First: the key from the .env file 
    key=os.environ.get("GEMINI_API_KEY", "")
    if key=="":
        return None #if there is no key we use the keywords function
    #Second: instructions for the AI 
    prompt=(
        "A family wrote what tutoring they need: \"" + sentence + "\"\n"
        "Our tutors teach these subjects: " + ", ".join(subjects) + "\n"
        "Answer ONLY with JSON like this:\n"
        "{\"subject\": \"Math\", \"days\": [\"Fri\", \"Sat\"], \"after\": 16, \"at\": null}\n"
        "subject: one subject from the list, or \"\" if none fits.\n"
        "days: short names Sat, Sun, Mon, Tue, Wed, Thu, Fri (weekend = Fri and Sat), or [] for any day.\n"
        "after / at: an hour from 0 to 23, or null. \"after 4\" means 16.\n"
        "The sentence can be in English or Arabic."
    )
    #third: send it to Gemini 
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"
    body={
        "contents":[{"parts":[{"text":prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    try:
        request=urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type":"application/json", "x-goog-api-key": key},
        )
        #the waiting time is never longer than 10 seconds 
        with urllib.request.urlopen(request, timeout=15) as response:
            answer=json.loads(response.read())
        #fourth: take the Ai's text out of the answer and turn it into a dictionary
        text=answer["candidates"][0]["content"]["parts"][0]["text"]
        data=json.loads(text)
    except urllib.error.HTTPError as error:
        print("Gemini error:", error.code, error.read().decode())
        return None
    except Exception as error:
        print("Gemini error:", error)
        return None

    #fifth: only keep the relevent values
    need={"subject":"", "days":[], "after":None, "at":None}
    if data.get("subject") in subjects:
        need["subject"]=data["subject"]
    for day in data.get("days") or[]:
        if day in DAYS.values() and day not in need["days"]:
            need["days"].append(day)
    for part in ["after", "at"]:
        hour=data.get(part)
        if type(hour)==int and 0<=hour<=23:
            need[part]=hour
    return need

#The AI is used first, if it fails use the keywords so this feature always works
def understand_need(sentence, subjects):
    need=gemini_helper(sentence, subjects)
    if need is not None:
        need["by"]="AI"
        return need
    need=keyword_helper(sentence,subjects)
    need["by"]="keywords"
    return need