#!/usr/bin/env python

import argparse
import json
from pkg_resources import resource_string, resource_filename
from mako.template import Template
from subprocess import call
from pprint import pprint

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def build_shared_parsers(body):
  parsers = {}
  for switch, sub_body in body.iteritems():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(sub_body['args']['long'], help=sub_body['args']['help'])
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
        csp.add_argument(arg_sub_body['long'], help=arg_sub_body['help'])

      attach_subparsers(csp, shared_parsers, sub_body, (level + 1))

def init(arg_vars):
  app_name = arg_vars['app-name']
  ansible_dir = app_name + "/deployments/ansible"

  print(bcolors.OKBLUE + "> Invoking Leiningen and streaming its output ..." + bcolors.HEADER)
  call(["lein", "new", "onyx-app", app_name])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished executing Leiningen." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Initializing deployment folders ...")
  call(["mkdir", "-p", (app_name + "/deployments")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished deployment folder initialization." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Initializing .engraver folders ..." + bcolors.ENDC)
  call(["mkdir", "-p", (app_name + "/.engraver")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished .engraver folder initialization." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Cloning Ansible playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "git@github.com:MichaelDrogalis/engraver-ansible.git", ansible_dir])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Initializing Ansible machines directory..." + bcolors.ENDC)
  call(["mkdir", "-p", (ansible_dir + "/vars/machine_profiles")])
  call(["mkdir", "-p", (ansible_dir + "/group_vars")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible machines directory creation." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Creating default Ansible playbook..." + bcolors.ENDC)
  engraver_playbook_file = resource_filename(__name__, "ansible_template/engraver_playbook.yml")
  call(["cp", engraver_playbook_file, (ansible_dir + "/engraver_playbook.yml")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default playbook creation." + bcolors.ENDC)

def cluster_new(arg_vars):
  ansible_dir = "deployments/ansible"

  print(bcolors.OKBLUE + "> Creating default Ansible machine profile..." + bcolors.ENDC)
  default_profile_file = resource_filename(__name__, "ansible_template/vars/machine_profiles/default_profile.yml")
  call(["cp", default_profile_file, (ansible_dir + "/vars/machine_profiles/default_profile.yml")])

  tpl = Template(resource_string(__name__, "ansible_template/group_vars/all.yml"))

  with open((ansible_dir + "/group_vars/" + arg_vars['cluster_name'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(cluster_name=arg_vars['cluster_name']))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default machine profile creation." + bcolors.ENDC)
  print("")

def main():
  parser = argparse.ArgumentParser(description = "Manages and deploys Onyx clusters.")
  data = json.loads(resource_string(__name__, 'args.json'))

  shared_parsers = build_shared_parsers(data['shared-parsers'])
  attach_subparsers(parser, shared_parsers, data, 0)

  args = parser.parse_args()
  arg_vars = vars(args)

  if (arg_vars.get('command-0') == 'init'):
    init(arg_vars)
  elif (arg_vars.get('command-0') == 'cluster'):
    if (arg_vars.get('command-1') == 'new'):
      cluster_new(arg_vars)
