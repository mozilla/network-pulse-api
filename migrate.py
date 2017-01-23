import json

json_data=open('./migrationData.json').read()
entries = json.loads(json_data)["Form Responses 1"]

massagedData = []

def stringify(oldKey):
    newData = entry[oldKey]
    if(type(newData) is list):
        newData = ', '.join(newData)
    return newData

def arrayify(oldKey):
    newData = entry[oldKey]
    if(type(newData) is str and len(newData) > 0):
        newData = [newData]
    if(len(newData) is 0):
        return []

    return newData

for entry in entries:
    newEntry = {}
    newEntry["created"] = entry["Timestamp"]

    featured = False
    if(entry["Featured"] == True):
        featured = True
    newEntry["featured"] = featured

    newEntry["title"] = stringify("Title")
    newEntry["creators"] = arrayify("Creators")
    newEntry["content_url"] = entry["URL"]
    newEntry["description"] = stringify("Description")
    newEntry["interest"] = stringify("Interest")
    newEntry["get_involved_url"] = entry["Get involved URL"]
    newEntry["get_involved"] = stringify("Get involved")
    newEntry["tags"] = arrayify("Tags")
    newEntry["issues"] = arrayify("Issues")
    newEntry["thumbnail_url"] = entry["Thumbnail URL"]
    newEntry["internal_notes"] = stringify("Network connection") + " Origin: " + stringify("Origin")

    massagedData.append(newEntry)

with open('massagedData.json', 'w') as outfile:
    json.dump(massagedData, outfile)

# print(massagedData)