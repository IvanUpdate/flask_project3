import json
import data

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data.teachers, f)
