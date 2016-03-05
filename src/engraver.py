#!/usr/bin/env python

import argparse
import json

import init_command
import cluster_command
import configure_command

from pkg_resources import resource_string
from os import listdir, walk, getcwd
from os.path import dirname

def engraver_root_dir(current_dir):
  if (current_dir == "/"):
    if ".engraver" in listdir(current_dir):
      return [True, current_dir]
    else:
      return [False, "fatal: Not an Engraver project (or any of the parent directories): .engraver"]
  else:
    if ".engraver" in listdir(current_dir):
      return [True, current_dir]
    else:
      return engraver_root_dir(dirname(current_dir))

def add_argument(parser, body):
  long_opt = [body['long']]

  opts = {}
  opts['help'] = body['help']
  if body.get('required'):
     opts['required'] = True

  apply(parser.add_argument, long_opt, opts)

def build_shared_parsers(body):
  parsers = {}
  for switch, sub_body in body.iteritems():
    parser = argparse.ArgumentParser(add_help=False)
    add_argument(parser, sub_body['args'])
    parsers[switch] = parser
  return parsers

def attach_subparsers(parent_parser, shared_parsers, body, level):
  dst = 'command-' + str(level)
  if body.get('commands'):
    sp = parent_parser.add_subparsers(help=body['help'], dest=dst)
    for sub_command, sub_body in body.get('commands').iteritems():
      my_shared_parsers = map(lambda x: shared_parsers[x], sub_body.get('shared-parsers', []))
      csp = sp.add_parser(sub_command, help=sub_body['help'], parents=my_shared_parsers)

      for arg, arg_sub_body in sub_body.get('args', {}).iteritems():
        add_argument(csp, arg_sub_body)

      attach_subparsers(csp, shared_parsers, sub_body, (level + 1))

fns = {("init",): init_command.init,
       ("configure", "aws"): configure_command.configure_aws,
       ("cluster", "new"): cluster_command.cluster_new,
       ("cluster", "describe"): cluster_command.cluster_describe,
       ("cluster", "provision"): cluster_command.cluster_provision,
       ("cluster", "machines", "new"): cluster_command.cluster_machines_new,
       ("cluster", "machines", "list"): cluster_command.cluster_machines_list,
       ("cluster", "machines", "describe"): cluster_command.cluster_machines_describe}

def main():
  parser = argparse.ArgumentParser(description = "Manages and deploys Onyx clusters.")
  data = json.loads(resource_string(__name__, 'args.json'))

  shared_parsers = build_shared_parsers(data['shared-parsers'])
  attach_subparsers(parser, shared_parsers, data, 0)

  args = parser.parse_args()
  arg_vars = vars(args)
  commands = ['command-0', 'command-1', 'command-2', 'command-3']
  command_seq = [ arg_vars.get(k) for k in commands if arg_vars.get(k) is not None ]

  [success, rets] = engraver_root_dir(getcwd())
  if (arg_vars.get('command-0') in ['init', 'configure']) or success:
    project_root = rets
    apply(fns.get(tuple(command_seq)), [arg_vars, project_root])
  else:
    print rets
