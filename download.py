#! /usr/bin/env python3
import json
import os
import requests
import sys

import config


def download_attachments(room_name, auth, page):
    for message in page:
        if message.get("attachments"):
            for att in message["attachments"]:
                if att.get("type") == "file":
                    file_name = "output/{}/files/{}".format(room_name, att["title"])
                    print("Downlaoding {}".format(file_name))
                    url = "{}{}".format(config.server, att["title_link"])
                    r = requests.get(url, headers=auth)
                    print(r.status_code)
                    with open(file_name, "wb") as fh:
                        fh.write(r.content)


def get_history(auth, room_name, room_type):
    history_endpoint = "{}/api/v1/{}s.history".format(config.server, room_type)

    print("Starting dowload")
    history = []
    params = {
        "roomName": room_name,
        "count": config.page_size,
        "offset": 0,
    }

    while True:
        print("Getting {} messages".format(config.page_size))
        r = requests.get(history_endpoint, params=params, headers=auth)
        page = r.json()["messages"]
        download_attachments(room_name, auth, page)
        history += page
        if len(page) == 0:
            # we got all messages when we reache the first empty page
            print("Downloaded all messages")
            return history
        params["offset"] += config.page_size


def identify_room(auth, room_name):
    # Get list of all visible channels
    r = requests.get("{}/api/v1/channels.list".format(config.server), headers=auth)
    data = r.json()
    if data["success"]:
        channel_names = [x["name"] for x in data["channels"]]
        if room_name in channel_names:
            print("Identified {} as a channel".format(room_name))
            return "channel"

    # Get list of all visible channels
    r = requests.get("{}/api/v1/groups.list".format(config.server), headers=auth)
    data = r.json()
    if data["success"]:
        group_names = [x["name"] for x in data["groups"]]
        if room_name in group_names:
            print("Identified {} as a group".format(room_name))
            return "group"

    print("Either {} doesn't exists, or it's a private group and you are not a member".format(room_name))
    sys.exit()


if __name__ == "__main__":
    room_name = sys.argv[1]
    if not room_name:
        print("Please provice a room name with './download.py <room name>'")
        sys.exit()

    auth = {"X-Auth-Token": config.token, "X-User-Id": config.user_id}
    room_type = identify_room(auth, room_name)

    try:
        os.mkdir("output")
    except FileExistsError:
        pass

    try:
        os.mkdir("output/{}".format(room_name))
        os.mkdir("output/{}/files".format(room_name))
    except FileExistsError:
        print("The folder for this room already exists. Please clean it up before running this script again")
        sys.exit()

    history = get_history(auth, room_name, room_type)
    filename = "output/{}/history.json".format(room_name)
    with open(filename, "w") as fh:
        json.dump(history, fh, indent=4)
    print("Saved history to: {}".format(filename))
