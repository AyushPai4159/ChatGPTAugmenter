import json

# Open and read the file
def exportData():
    docs: dict = {}
    try:
        with open("../../uploadData/conversations.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        print("❌ Error: Could not open conversations.json file")
        print("📁 Please make sure to upload your conversations.json file to the uploadData/ directory in the root")
        print("💡 Steps to fix this:")
        print("   1. Export your ChatGPT conversations from https://chat.openai.com/")
        print("   2. Extract the conversations.json file from the downloaded archive")
        print("   3. Create an 'uploadData' directory in the root of the project")
        print("   4. Place conversations.json in the uploadData/ directory")
        print(f"🔍 Technical details: {e}")
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        print("❌ Error: conversations.json file is not valid JSON")
        print("🔧 Please ensure the file is a valid ChatGPT export")
        print(f"🔍 Technical details: {e}")
        raise SystemExit(1)

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


