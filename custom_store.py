#!/bin/env python3
# coding: utf-8
import datetime
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return {"@IS_A_SET":list(obj)}
        if isinstance(obj, datetime.datetime):
            return {"@IS_A_TS": obj.timestamp()}
        return json.JSONEncoder.default(self, obj)

class JSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.set_object_hook
        super(JSONDecoder, self).__init__(*args, **kwargs)

    def set_object_hook(self, obj):
        if isinstance(obj, dict) and '@IS_A_SET' in obj:
            return set(obj["@IS_A_SET"])
        if isinstance(obj, dict) and '@IS_A_TS' in obj:
            return datetime.datetime.fromtimestamp(obj['@IS_A_TS'])
        else:
            return obj

def load(fname):
    try:
        return json.load(open("standup_data.json","r"),cls=JSONDecoder)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save(obj,fname):
    json.dump(obj, open("standup_data.json","w"), cls=JSONEncoder)
