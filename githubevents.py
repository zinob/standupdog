#!/bin/env python3
# coding: utf-8

import requests
import datetime
from read_config import config

def _guess_when():
    if datetime.datetime.now().weekday()==0:
        frm=datetime.datetime.now() - datetime.timedelta(days=3)
    else:
        frm=datetime.datetime.now() - datetime.timedelta(days=1)
    return frm

def _gh_to_datetime(s):
    return datetime.datetime.strptime(s,"%Y-%m-%dT%H:%M:%SZ")

def _get_events(since,api_token):
    l=[]
    for i in range(1,10):
        r=requests.get("https://api.github.com/users/zinob/events/orgs/zensum?page=%i"%i,headers={"Authorization":"token "+api_token})
        events=((_gh_to_datetime(i["created_at"]),i["actor"]["login"],i["repo"]["name"]) for i in r.json())
        for event in events:
            if (event[0] - since).total_seconds() > 0:
                yield event
            else:
                break

def get_events_per_user(since):
    events=_get_events(since,config.github.api_token)
    usermap = config.github.github_slack_user_map
    d={}
    unknown = []
    last=datetime.datetime.fromtimestamp(0)
    for (t,k,v) in events:
        if k not in usermap:
            unknown.append(k)
            continue
        d.setdefault(usermap[k.lower()],set()).add(v.split("/",1)[1])
        last=max(last,t)
    return d, last, unknown

if __name__ == "__main__":
    print(get_events_per_user(_guess_when()))
