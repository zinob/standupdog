#!/bin/env python3
# coding: utf-8

import shelve
import textwrap
import slacklogs
import githubevents

import read_config

#####################################
# https://cdn-shop.adafruit.com/datasheets/CSN-A2+User+Manual.pdf
# ESC @ #init printer
# ESC R 5 # set swedish 
# ESC GS & # create custom character (page 26)
# ESC % 0x01 # activate user characters
# ESC t 16 # set code-page latin-1
# ESC % 0x01 =  1B2501 #set user chars
# Underline: echo 1B2D02

#initseq
printer_ctl={
 "init":b'\x1B\x40', #init
 "latin":b'\x1B\x74\x10', #set latin1
 "fonta":b'\x1B\x21\x00', #font A
 "fontb":b'\x1B\x21\x01', #font B
 "underlineon":b'\x1B\x2D\x02',
 "underlineoff":b'\x1B\x2D\x00',
}

def ul(s):
 return printer_ctl["underlineon"] +s+ printer_ctl["underlineon"]

def big(s):
 return printer_ctl["fonta"] +s+ printer_ctl["fontb"]

storage = shelve.open("standup_data.shelve",writeback=True)
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
    raw=(" @%s "%name).center(LINE_WIDTH*6//8,"-") + "\n"
    return  b"\n"+big(raw.encode("latin-1")) 

def format_fields(who,log_entry,message_map):
    return format_name_header(who) +\
        "\n".join( line_wrap(formatter(log_entry[key])) for key,formatter in message_map if log_entry.get(key,None)).encode("latin-1","replace")

import datetime
frm=datetime.datetime.now() - datetime.timedelta(days=3)
print("starting")
slacklog = slacklogs.get_todays_events(frm).items()
print("got slacklog")
if len(slacklog) > 0:
#    unknown_gh = update_gh_since_last(storage)
    print("github fetched")
    with open("printout.txt","bw") as f:
        f.write(b"\n".join(todays_standup(slacklog,storage)))
        print("Write standup")
        f.write(b"\n")
        print("wrote linefeed")
        if unknown_gh:
            f.write(b"new guys on GitHub: \n" + "\n   ".join(unknown_gh).encode('latin-1',"replace"))
            print("found and talked about new guys on github")
        f.write(b"\n\n")
        print("wrote linefeed, going to close file...")
print("closed file")

