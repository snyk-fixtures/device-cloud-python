#!/usr/bin/env python

import argparse
import json
import os
import sys

if sys.version_info.major == 2:
    input = raw_input

file_desc = "\nName of config file to write (eg. appname-connect.cfg) (Required)"
cloud_desc = "\nCloud host address (Required)"
port_desc = "\nCloud port (eg. 1883/8883/443) (Required)"
token_desc = "\nCloud token (Required)"
do_validate_desc = "\n Validate SSL certificates (default true) (Optional)"
no_validate_desc = "\nDo not validate SSL certificates (Optional)"
cert_desc = "\nLocation of an ssl certificate bundle (If not set will use the bundle included with certifi instead) (Optional)"

def generate():
    parser = argparse.ArgumentParser(description="Generate a connection config file. Give no arguments to run with prompt.")
    parser.add_argument("-f", "--file", help=file_desc)
    parser.add_argument("-c", "--cloud", help=cloud_desc)
    parser.add_argument("-p", "--port", type=int, help=port_desc)
    parser.add_argument("-t", "--token", help=token_desc)
    parser.add_argument("-n", "--no-validate", help=no_validate_desc, dest='validate', action="store_false", default=True)
    parser.add_argument("-s", "--ssl-bundle", help=cert_desc)

    args = parser.parse_args(sys.argv[1:])
    file_name = ""
    config = {"cloud":{}}

    if len(sys.argv) > 1:
        # Arguments given. Attempt to use these arguments.
        missing = []
        if args.file:
            file_name = args.file
        else:
            missing.append("file name")
        if args.cloud:
            config["cloud"]["host"] = args.cloud
        else:
            missing.append("cloud address")
        if args.port:
            config["cloud"]["port"] = args.port
        else:
            missing.append("port")
        if args.token:
            config["cloud"]["token"] = args.token
        else:
            missing.append("token")

        if missing:
            print("Missing {}. Try again.".format(", ".join(missing)))
            return 1

        config["validate_cloud_cert"] = args.validate
        if args.ssl_bundle:
            config["ca_bundle_file"] = args.ssl_bundle

    else:
        # No arguments. Use prompt to gather information.
        print("Generating config. Please enter connection information for the config file.")
        print(file_desc)
        file_name = input("# ").strip()
        if not file_name:
            print("File name is required.")
            return 1
        if not os.path.splitext(file_name)[1]:
            file_name += ".cfg"

        print(cloud_desc)
        temp = input("# ").strip()
        if temp:
            config["cloud"]["host"] = temp
        else:
            print("Cloud address is required.")
            return 1

        print(port_desc)
        temp = input("# ").strip()
        if temp:
            if temp.isdigit():
                config["cloud"]["port"] = int(temp)
            else:
                print("Cloud port must be an integer.")
                return 1
        else:
            print("Cloud port is required.")
            return 1

        print(token_desc)
        temp = input("# ").strip()
        if temp:
            config["cloud"]["token"] = temp
        else:
            print("Cloud token is required.")
            return 1

        print(do_validate_desc)
        temp = input("# ").strip()
        if temp:
            negatives = ["false", "f", "no", "n"]
            positives = ["true", "t", "yes", "y"]

            if temp.lower() in negatives:
                config["validate_cloud_cert"] = False
            else:
                config["validate_cloud_cert"] = True
                if temp.lower() not in positives:
                    print("Not recognised. Defaulting to True.")
        else:
            config["validate_cloud_cert"] = True

        print(cert_desc)
        temp = input("# ").strip()
        if temp:
            config["ca_bundle_file"] = temp

    with open(file_name, "w+b") as config_file:
        config_file.write(json.dumps(config, indent=2, sort_keys=True).encode())
    print("\nConfiguration:")
    print(json.dumps(config, indent=2, sort_keys=True))
    print("")
    if len(sys.argv) == 1:
        input("Press enter to finish...")
    return 0


if __name__ == "__main__":
    status = generate()
    sys.exit(status)
