#!/bin/bash

cd ..
cd pythonFiles
# Run first Python script
python3 parseJson.py

# Run second Python script
python3 preload.py

# Run third Python script
python3 createDoc.py

