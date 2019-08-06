#!/usr/bin/python3

import argparse
import subprocess

from html.parser import HTMLParser
from enum import Enum

class ParsingStep(Enum):
    FINDING_TABLE = 0
    PARSING_TABLE = 1
    PARSING_CELL = 2


class MyHTMLParser(HTMLParser):
    TABLE_ID_STRING="Current Address Table"
    search_step=ParsingStep.FINDING_TABLE
    cell_count=0

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
                print(data,end=",")
                self.cell_count+=1
                if(self.cell_count==3):
                    print("")
                    self.cell_count=0


html_parser = MyHTMLParser()
# arg_parser = argparse.ArgumentParser()
# arg_parser.add_argument("filename")
# cli_args = arg_parser.parse_args()
# with open(cli_args.filename, 'r') as f:
cmd="wget --http-user=admin --http-password=canonical --output-document=- http://10.228.0.21/dynamic_address.html"
with subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE) as wget_stdout:
   html_parser.feed(wget_stdout.stdout.read())
proc.stdout.close()


