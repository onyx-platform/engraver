#!/usr/bin/env python

import argparse
import json
import yaml
from pkg_resources import resource_string, resource_filename
from mako.template import Template
from subprocess import call
from os import listdir, walk
from os.path import isfile, join
from prettytable import PrettyTable
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
  ansible_dir = app_name + "/ansible"

  print(bcolors.OKBLUE + "> Invoking Leiningen and streaming its output ..." + bcolors.HEADER)
  call(["lein", "new", "onyx-app", app_name])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished executing Leiningen." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Initializing .engraver folders ..." + bcolors.ENDC)
  call(["mkdir", "-p", (app_name + "/.engraver")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished .engraver folder initialization." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Cloning Ansible playbook from Git. Streaming Git output ..." + bcolors.HEADER)
  call(["git", "clone", "git@github.com:MichaelDrogalis/engraver-ansible.git", ansible_dir])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished cloning playbook." + bcolors.ENDC)
  print("")
  
  print(bcolors.OKBLUE + "> Initializing Ansible vars directories..." + bcolors.ENDC)
  call(["mkdir", "-p", (ansible_dir + "/group_vars")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible vars directory creation." + bcolors.ENDC)
  print("")

  print(bcolors.OKBLUE + "> Creating default Ansible playbook..." + bcolors.ENDC)
  engraver_playbook_file = resource_filename(__name__, "ansible_template/engraver_playbook.yml")
  call(["cp", engraver_playbook_file, (ansible_dir + "/engraver_playbook.yml")])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default playbook creation." + bcolors.ENDC)

def cluster_new(arg_vars):
  print(bcolors.OKBLUE + "> Creating default Ansible machine profile..." + bcolors.ENDC)
  default_profile_file = resource_filename(__name__, "ansible_template/cluster_vars/machine_profiles/default_profile.yml")
  call(["mkdir", "-p", ("ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles")])
  call(["cp", default_profile_file, "ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles/default_profile.yml"])

  tpl = Template(resource_string(__name__, "ansible_template/group_vars/all.yml"))

  with open(("ansible/group_vars/" + arg_vars['cluster_name'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(cluster_name=arg_vars['cluster_name']))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default machine profile creation." + bcolors.ENDC)
  print("")

def cluster_describe(arg_vars):
  path = "ansible/cluster_vars"
  clusters = next(walk(path))[1]
  t = PrettyTable(['Cluster Name'])
  t.align = "l"

  for c in clusters:
    t.add_row([c])

  print t

def cluster_machines_describe(arg_vars):
  path = "ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles"
  files = [f for f in listdir(path) if isfile(join(path, f))]
  t = PrettyTable(['Profile ID', 'N Instances', 'Services'])
  t.align["Profile ID"] = "l"
  t.align["Services"] = "l"
  for f in files:
    with open(path + "/" + f, 'r') as stream:
      content = yaml.load(stream)
      t.add_row([content['profile_id'], content['n_machine_instances'], ", ".join(content['machine_services'])])
  print t

def cluster_machines_new(arg_vars):
  print(bcolors.OKBLUE + "> Creating new Ansible machine profile..." + bcolors.ENDC)
  tpl = Template(resource_string(__name__, "ansible_template/cluster_vars/machine_profiles/profile_template.yml"))

  with open(("ansible/cluster_vars/" + arg_vars['cluster_name'] +
             "/machine_profiles/" + arg_vars['profile_id'] +
             "_profile.yml"), "w") as text_file:
    text_file.write(tpl.render(profile_id=arg_vars['profile_id'],
                               n_instances=arg_vars['n'],
                               services=[x.strip() for x in arg_vars['services'].split(",")]))

  tpl = Template(resource_string(__name__, "ansible_template/engraver_playbook.yml"))
  path = "ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]
  with open(("ansible/engraver_playbook.yml"), "w") as text_file:
    text_file.write(tpl.render(profiles=profile_files))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible machine profile creation." + bcolors.ENDC)

def cluster_provision(arg_vars):
  pass

fns = {("init",): init,
       ("cluster", "new"): cluster_new,
       ("cluster", "describe"): cluster_describe,
       ("cluster", "provision"): cluster_provision,
       ("cluster", "machines", "new"): cluster_machines_new,
       ("cluster", "machines", "describe"): cluster_machines_describe}

def main():
  parser = argparse.ArgumentParser(description = "Manages and deploys Onyx clusters.")
  data = json.loads(resource_string(__name__, 'args.json'))

  shared_parsers = build_shared_parsers(data['shared-parsers'])
  attach_subparsers(parser, shared_parsers, data, 0)

  args = parser.parse_args()
  arg_vars = vars(args)
  commands = ['command-0', 'command-1', 'command-2', 'command-3']
  command_seq = [ arg_vars.get(k) for k in commands if arg_vars.get(k) is not None ]

  apply(fns.get(tuple(command_seq)), [arg_vars])
