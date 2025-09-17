import json

# 加载json
target='search_api.json'
with open(target, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 打印json数据
print(data)