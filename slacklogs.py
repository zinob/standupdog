#!/bin/env python3
# coding: utf-8

import requests
import datetime
from read_config import config

slack_URL="https://slack.com/api/channels.history"


def _get_chanel_log(from_time, slack_token, channel_id):
    return requests.get(slack_URL,params={"token":slack_token,"channel":channel_id,"oldest":from_time})

def slack_uid_uname_map(token):
    slack_users=requests.get("https://slack.com/api/users.list",params={"token":token})
    return {i['id']:i["name"] for i in slack_users.json()['members']}

def _get_message_attachments(slack_log):
    messages=slack_log["messages"]
    for message in sorted(messages,key=lambda x:x["ts"]):
        is_standupbot="standup" in message.get('username',None).lower()
        has_attachments="attachments" in message
        if is_standupbot and has_attachments:
            yield message["attachments"]
        elif not has_attachments:
            pass #should probbably get TS here...
            #print(message)

def _build_stories(attachment_list):
    stories={}
    pre="unknown"
    for i in attachment_list:
        for j in i:
            pre=j.get("pretext",pre)
            if not "fields" in j:
                field={"title":j["title"], "value":j["text"]}
            else:
                f=j["fields"][0]
                field={"title":f["title"], "value":f["value"]}
            stories.setdefault(pre,[]).append(field)
    return stories

def _classify_section(section):
    parttypes={"diskutera":"also","idag":"today","sist":"last","hindrar":"block"}
    for k,v in parttypes.items():
        if k in section["title"]:
            return v

def _tidy_up_stories(stories,user_map):
    tidy_stories = {}
    for who,parts in stories.items():
        uid=who[2:-1]
        uname=user_map.get(uid,"unknown")
        for part in parts:
            section=_classify_section(part)
            text= part["value"].strip()
            if len(text) > 1 and text.lower().replace(".","") not in ["nope","nej","nix"]: 
                tidy_stories.setdefault(uname,{})[section] = text
    return tidy_stories

def get_todays_events(today_begins_at=None):
    """Returns a map of user to things-they-said
    if today_begins_at is not defined it will be set to "now - 1 day"
    """

    if today_begins_at == None:
        startat = (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()
    elif hasattr(today_begins_at, "timestamp"):
        startat = today_begins_at.timestamp()
    else:
        startat = today_begins_at

    token = config.slack.api_token
    channel_id = config.slack.chanel_id

    slack_log = _get_chanel_log(startat, token, channel_id)
    ulist = slack_uid_uname_map(token)

    attachlist = _get_message_attachments(slack_log.json())
    stories = _build_stories(attachlist)
    return _tidy_up_stories(stories,ulist)

def main():
    print(get_todays_events())

if __name__=="__main__":
    main()
