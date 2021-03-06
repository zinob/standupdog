#!/usr/bin/env python3
# coding: utf-8

import textwrap
import slacklogs
import githubevents

import read_config
import custom_store

#####################################
# https://cdn-shop.adafruit.com/datasheets/CSN-A2+User+Manual.pdf
# ESC @ #init printer
# ESC R 5 # set swedish 
# ESC GS & # create custom character (page 26)
# ESC % 0x01 # activate user characters
# ESC t 16 # set code-page latin-1
# ESC % 0x01 =  1B2501 #set user chars
# Underline: echo 1B2D02
# ESC J n = 1B 4A # feed paper nx0.125 mm 

#initseq
printer_ctl={
 "init":b'\x1B\x40', #init
 "latin1":b'\x1B\x74\x10', #set latin1
 "fonta":b'\x1B\x21\x00', #font A
 "fontb":b'\x1B\x21\x01', #font B
 "underlineon":b'\x1B\x2D\x02',
 "underlineoff":b'\x1B\x2D\x00',
 "feed":b'\x1B\x4A'+bytes(chr(5*8),"latin-1")
}

def ul(s):
 return printer_ctl["underlineon"] +s+ printer_ctl["underlineoff"]

def big(s):
 return printer_ctl["fonta"] +s+ printer_ctl["fontb"]


storage = custom_store.load("standup_data.json")

LINE_WIDTH = 41 
INDENT_WIDTH = 4

def update_gh_since_last(storage):
    #del storage["gh_last"]
    gh_events, gh_last, unknown_users = githubevents.get_events_per_user(storage.get("gh_last",githubevents._guess_when()))
    storage["gh_last"] = gh_last

    for user,repos in gh_events.items():
        u=storage.get(user,{})
        u["github"]=u.get("github",set()).union(repos)
        storage["user"]=u

    return unknown_users

message_map=([
    ("today",lambda s: "Idag: " +s),
    ("last",lambda s: "Sedan igår: "+s),
    ("promised",lambda s: "Min plan igår: "+s),
    ("github",lambda st: "GitHub: "+", ".join(sorted(st))),
    ("block",lambda s: "Hinder: "+s),
    ("also",lambda s: "För övrigt: "+s),
])

def line_wrap(s):
    return "\n".join(textwrap.wrap(s,LINE_WIDTH,subsequent_indent=" "*INDENT_WIDTH))

def todays_standup(slacklog,storage):
    for user, events in slacklog:
        ulog=storage.setdefault(user,{})
        today = {
                "promised":ulog.get("promised",None),
                "github":ulog.get("github",None)
        }
        ulog["promised"] = events["today"]
        today.update(events)
        yield format_fields(user,today,message_map)
        ulog["github"] = set()
        storage[user] = ulog

def format_name_header(name):
    raw=(" @%s "%name).center(LINE_WIDTH*6//8,"-")
    return  b"\n"+big(raw.encode("latin-1"))  + b"\n"

def ul_field_name(s):
	head, tail = s.split(b":",1)
	return ul(head) + tail

def format_fields(who,log_entry,message_map):
    return format_name_header(who) +\
        b"\n".join( ul_field_name(line_wrap(formatter(log_entry[key])).encode("latin-1","replace")) for key,formatter in message_map if log_entry.get(key,None))

#import datetime
#frm=datetime.datetime.now() - datetime.timedelta(days=3)
slacklog = slacklogs.get_todays_events().items()
if len(slacklog) > 0:
    unknown_gh = update_gh_since_last(storage)
    with open("/tmp/printout.txt","bw") as f:
        f.write(printer_ctl['init']+printer_ctl['latin1'])
        f.write(b"\n".join(todays_standup(slacklog,storage)))
        f.write(b"\n")
        if unknown_gh:
            f.write(b"new guys on GitHub: \n" + "\n   ".join(unknown_gh).encode('latin-1',"replace"))
        f.write(printer_ctl["feed"])

storage = custom_store.save(storage,"standup_data.json")

