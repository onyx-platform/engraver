#!/usr/bin/env python

import argparse
import json
from pprint import pprint

parser = argparse.ArgumentParser(description = "Manages and deploys Onyx clusters")

with open('args.json') as data_file:    
  data = json.load(data_file)

def attach_subparsers(parent_parser, body):
  if body.get('commands'):
    sp = parent_parser.add_subparsers(help=body['help'])
    for sub_command, sub_body in body.get('commands').iteritems():
      csp = sp.add_parser(sub_command, help=sub_body['help'])

      for arg, arg_sub_body in sub_body.get('args', {}).iteritems():
        csp.add_argument(arg_sub_body['long'], help=arg_sub_body['help'])

      attach_subparsers(csp, sub_body)
    
attach_subparsers(parser, data)

args = parser.parse_args()
arg_vars = vars(args)
