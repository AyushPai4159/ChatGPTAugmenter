import json

# Open and read the file
def exportData():
    docs: dict = {}
    with open("../data/conversations.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Now `data` is a Python object (usually a list or dict)


    for point in data: 


        pointers = point['mapping']
        keys = pointers.keys()
        user: str = "dummy"
        for key in keys:
            value = pointers[key]
            if value['message'] != None:
                content = value['message']['content']
                text = ""
                if 'parts' in content:
                    text = str(content['parts'][0])
                elif 'text' in content:
                    text = str(content['text'])
                role: str = value['message']['author']['role']
                if role == "user":
                    user = text
                elif role != "system":
                    docs[user] = text


        
    return docs










data = exportData()

print(data)
with open("../data/output.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"JSON data saved to {json_file}")


