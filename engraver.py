#!/usr/bin/env python

import argparse
import json
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

parser = argparse.ArgumentParser(description = "Manages and deploys Onyx clusters.")

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

print(bcolors.OKBLUE + "> Invoking Leiningen and streaming its output ..." + bcolors.HEADER)
call(["lein", "new", "onyx-app", "my-app"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished executing Leiningen." + bcolors.ENDC)
print("")

print(bcolors.OKBLUE + "> Initializing deployment folders ...")
call(["mkdir", "-p", "my-app/deployments"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished deployment folder initialization." + bcolors.ENDC)
print("")

print(bcolors.OKBLUE + "> Initializing .engraver folders ..." + bcolors.ENDC)
call(["mkdir", "-p", "my-app/.engraver"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished .engraver folder initialization." + bcolors.ENDC)
print("")

print(bcolors.OKBLUE + "> Cloning Ansible playbook from Git. Streaming Git output ..." + bcolors.HEADER)
call(["git", "clone", "git@github.com:MichaelDrogalis/engraver-ansible.git", "my-app/deployments/ansible"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
print("")

print(bcolors.OKBLUE + "> Initializing Ansible machines directory..." + bcolors.ENDC)
call(["mkdir", "-p", "my-app/deployments/ansible/vars/machine_profiles"])
call(["mkdir", "-p", "my-app/deployments/ansible/group_vars"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible machines directory creation." + bcolors.ENDC)
print("")

print(bcolors.OKBLUE + "> Creating default Ansible machine profile..." + bcolors.ENDC)
call(["cp", "ansible/vars/machine_profiles/default_profile.yml", "my-app/deployments/ansible/vars/machine_profiles/default_profile.yml"])
call(["cp", "ansible/group_vars/all.yml", "my-app/deployments/ansible/group_vars/all.yml"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default machine profile creation." + bcolors.ENDC)
print("")

print(bcolors.OKBLUE + "> Creating default Ansible playbook..." + bcolors.ENDC)
call(["cp", "ansible/engraver_playbook.yml", "my-app/deployments/ansible/engraver_playbook.yml"])
print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default playbook creation." + bcolors.ENDC)
