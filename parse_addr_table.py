#!/usr/bin/python3

import argparse
import subprocess
import yaml
import re

from html.parser import HTMLParser
from enum import Enum

mac_addr_table=[]

switches= ["resnik", "gilbert"]

class ParsingStep(Enum):
    FINDING_TABLE = 0
    PARSING_TABLE = 1
    PARSING_CELL = 2

class MyHTMLParser(HTMLParser):
    TABLE_ID_STRING="Current Address Table"
    search_step=ParsingStep.FINDING_TABLE
    cell_count=0
    addr_row=[]

    def add_switch_name(self,switch):
        self.switch_name=switch
        self.addr_row=[switch]

# Check that we've really got a (vlan, MAC, port) triple, and add it to mac_addr_table
    def validate_and_add_row(self,row):
        row[2]=re.sub(':','',row[2])  # Remove ':' to normalise MAC format across different switches
        row[2]=row[2].upper()         # Translate to uppercase to normalise across switches
        if(len(row[2])==12):
            mac_addr_table.append(row.copy())

    def handle_starttag(self, tag, attrs):
        if((self.search_step == ParsingStep.PARSING_TABLE) and (tag == "tr")):
            self.search_step=ParsingStep.PARSING_CELL

    def handle_endtag(self, tag):
        if((self.search_step == ParsingStep.PARSING_CELL) and (tag == "tr")):
            self.search_step=ParsingStep.PARSING_TABLE

    def handle_data(self, data):
        if((self.search_step == ParsingStep.FINDING_TABLE) and (self.TABLE_ID_STRING in data)):
            self.search_step=ParsingStep.PARSING_TABLE
        if(self.search_step == ParsingStep.PARSING_CELL):
            if(not data.isspace()):
                self.addr_row.append(data)
                self.cell_count+=1
                if(self.cell_count==3):
                    self.validate_and_add_row(self.addr_row)
                    self.cell_count=0
                    self.addr_row=[self.switch_name]
#                    self.addr_row.clear()


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("filename")
cli_args = arg_parser.parse_args()

with open(cli_args.filename) as f:
    machines = yaml.safe_load(f)

for switch in switches:
    address=machines[switch]["interfaces"]["eth0"]["address"]
    username=machines[switch]["user"]
    password=machines[switch]["password"]
    print(address, username, password)

    cmd="wget --http-user="+username+" --http-password="+password+" --output-document=- http://"+address+"/dynamic_address.html"
    html_parser = MyHTMLParser()
    html_parser.add_switch_name(switch)
    with subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE) as wget_stdout:
        line_in_bytes=wget_stdout.stdout.read()
        html_parser.feed(line_in_bytes.decode("utf-8"))

print(mac_addr_table)

# Note: think about close()
