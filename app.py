from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "keys.json"

def load_keys():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    key = data.get('key', '').strip().upper()
    keys = load_keys()
    
    if key not in keys:
        return jsonify({"success": False, "message": "卡密无效"})
    
    key_data = keys[key]
    if isinstance(key_data, bool):
        if key_data is True:
            return jsonify({"success": False, "message": "卡密已被使用"})
        return jsonify({"success": True, "message": "验证通过"})
    
    if key_data.get("used", False):
        return jsonify({"success": False, "message": "卡密已被使用"})
    
    expire_ts = key_data.get("expire_timestamp", -1)
    if expire_ts != -1 and expire_ts < int(datetime.now().timestamp()):
        return jsonify({"success": False, "message": "卡密已过期"})
    
    return jsonify({"success": True, "message": "验证通过"})

@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_json()
    key = data.get('key', '').strip().upper()
    device_id = data.get('device_id', '')
    
    keys = load_keys()
    if key not in keys:
        return jsonify({"success": False, "message": "卡密无效"})
    
    key_data = keys[key]
    if isinstance(key_data, bool):
        if key_data is True:
            return jsonify({"success": False, "message": "卡密已被使用"})
        keys[key] = True
    else:
        if key_data.get("used", False):
            return jsonify({"success": False, "message": "卡密已被使用"})
        keys[key]["used"] = True
        keys[key]["used_by"] = device_id
        keys[key]["used_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(DATA_FILE, "w") as f:
        json.dump(keys, f, indent=2)
    
    return jsonify({"success": True, "message": "激活成功"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
