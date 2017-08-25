#!/usr/bin/env python

'''
Copyright (c) 2016-2017 Wind River Systems, Inc. 
 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
       http://www.apache.org/licenses/LICENSE-2.0
 
Unless required by applicable law or agreed to in writing, software  distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied.
'''

"""
Simple utility to create OTA packages from user input.
"""
import argparse
import json
import os
import random
import signal
import string
import sys
import tarfile
import zipfile
import helix.osal as osal

BADFILECHARS = [':', '/', '\\', '?', '"', '<', '>', '|', '%']

def sighandler(signum, frame):
    """
    Signal handler for exiting app.
    """
    global running
    print("Received signal {}, stopping application...".format(signum))
    exit(130)

def do_input(prompt):
    ver = sys.version_info[0]
    if ver == 2:
        return raw_input(prompt)
    elif ver == 3:
        return input(prompt)
    else:
        raise IOError("No input processor found.")

def generateManifest(args):
    manifest = {
                "name": args.name,
                "version": args.version,
                "description": args.description,
                "install": args.install,
                "reboot": args.reboot
               }
    if args.pre_install:
        manifest["pre_install"] = args.pre_install

    if args.post_install:
        manifest["post_install"] = args.post_install

    if args.error_action:
        manifest["error_action"] = args.error_action

    data = json.dumps(manifest)

    tmpname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    try:
        with open(tmpname, "w") as file:
            file.write(data)
            file.flush()
    except OSError as e:
        print(e)
        print("Error generating manifest!")
        os.remove(tmpname)
        tmpname = ""

    return tmpname


def promptParameters(args):
    if args.headless:
        return args

    while not args.name:
        args.name = do_input("Package Name: ")
        if not args.name:
            print("This is a required parameter!")

    while not args.version:
        args.version = do_input("Package Version: ")
        if not args.version:
            print("This is a required parameter!")

    if not args.description:
        args.description = do_input("Package Description (optional): ")

    if not args.pre_install:
        args.pre_install = do_input("Pre-install command (optional): ")

    while not args.install:
        args.install = do_input("Install command: ")
        if not args.install:
            print("This is a required parameter!")

    if not args.post_install:
        args.post_install = do_input("Post-install command (optional): ")

    if not args.error_action:
        args.error_action = do_input("Error action command (optional): ")

    if not args.reboot:
        valid = False
        while not valid:
            args.reboot = do_input("Reboot device after install\n"
                                    "(yes/no): ")
            args.reboot = args.reboot.lower()
            valid = args.reboot in ("yes", "no")
            if not valid:
                print("Invalid selection ({})!".format(args.reboot))

    if not args.files:
        fileno = 1
        files = []
        files.append(do_input("Additional Files to package ({}): ".format(fileno)))
        while files[fileno - 1] != "":
            fileno += 1
            files.append(do_input("Additional Files to package ({}): ".format(fileno)))

        args.files = files

    while not args.tar and not args.zip:
        pkg = do_input("Package type (zip or tar): ").lower()
        if pkg == "tar":
            args.tar = True
        elif pkg == "zip":
            args.zip = True
        elif pkg == "":
            print("This is a required parameter!")
        else:
            print("Invalid selection! Choose either zip or tar")

    return args


def createPackage(args):
    result = False
    manifest = generateManifest(args)
    filename = escapeName(args.name)
    archive = None
    try:
        if args.tar:
            filename += ".tar.gz"
            archive = tarfile.open(filename, 'w:gz')
            archive.add(manifest, "update.json")
            for file in args.files:
                if file:
                    archive.add(file)
            archive.close()
            result = True
        elif args.zip:
            filename += ".zip"
            archive = zipfile.ZipFile(filename, 'w')
            archive.write(manifest, "update.json")
            for file in args.files:
                if file:
                    archive.write(file)

            archive.close()
            result = True
        else:
            result = False
    except OSError as e:
            print(e)
            print("Package generation error!")
            if archive:
                os.remove(filename)
            result = False

    os.remove(manifest)

    return result

def escapeName(name):
    name = name.lower()
    for c in BADFILECHARS:
        name = name.replace(c, "")
    name = name.replace(" ", "_")
    return name

def validateArgs(args):
    valid = True
    valid = valid and args.name
    valid = valid and args.install
    valid = valid and args.version
    valid = valid and (args.tar or args.zip)
    valid = valid and args.reboot
    return valid

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sighandler)
    if osal.LINUX:
        signal.signal(signal.SIGQUIT, sighandler)

    # Parse command line arguments for easy (scriptable) package creation
    parser = argparse.ArgumentParser(description="HDC OTA Package Creator")

    parser.add_argument("-d", "--description", help="Package description")
    parser.add_argument("-e", "--error_action", help="Command to run on error")
    parser.add_argument("-f", "--files", help="Extra files to include "
                                               "(comma-separated string)")
    parser.add_argument("-H", "--headless", help="No prompt for missing parameters, fail instead", action='store_true')
    parser.add_argument("-i", "--install", help="Install command")
    parser.add_argument("-n", "--name", help="Package name")
    parser.add_argument("-p", "--pre_install", help="Pre-install command")
    parser.add_argument("-P", "--post_install", help="Post-install command")
    parser.add_argument("-r", "--reboot", help="Reboot after package install", action='store_true')
    parser.add_argument("-t", "--tar", help="Package into tar format", action='store_true')
    parser.add_argument("-v", "--version", help="Package version")
    parser.add_argument("-z", "--zip", help="Package into zip format", action='store_true')

    args = parser.parse_args(sys.argv[1:])
    if args.files:
        args.files = args.files.split(',')
    elif args.headless:
        args.files = []

    # Convert reboot to valid update.json string
    if args.reboot:
        args.reboot = "yes"
    elif args.headless:
        args.reboot = "no"

    # Change description to be empty if not specified during headless run
    if args.headless and not args.description:
        args.description = ""

    args = promptParameters(args)

    if not validateArgs(args):
        print("Invalid arguments supplied!")
        exit(1)

    if(createPackage(args)):
        fname = "{}.{}".format(escapeName(args.name), "zip" if args.zip else "tar.gz")
        print("Package {} created successfully!".format(fname))
        exit(0)
    else:
        print("Package creation failed!")
        exit(1)
