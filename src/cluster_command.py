#!/usr/bin/env python

import json
import yaml
import ConfigParser

from pkg_resources import resource_filename, resource_string
from prettytable import PrettyTable
from mako.template import Template
from os.path import isfile, join, expanduser, exists
from os import listdir, walk, chdir
from subprocess import call
from colors import bcolors

from ansible import invoke_ansible, refresh_playbook

def cluster_new(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Creating default Ansible playbook..." + bcolors.ENDC)
  default_profile_file = resource_filename(__name__, "ansible_template/vars/cluster_vars/machine_profiles/default_profile.yml")
  call(["mkdir", "-p", (project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles")])
  call(["cp", default_profile_file, project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles/default_profile.yml"])

  tpl = Template(resource_string(__name__, "ansible_template/group_vars/all.yml"))

  with open((project_root + "/ansible/group_vars/" + arg_vars['cluster_id'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(cluster_id=arg_vars['cluster_id']))

  refresh_playbook(arg_vars, project_root)

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible playbook creation." + bcolors.ENDC)
  print("")

def cluster_describe(arg_vars, project_root):
  path = project_root + "/ansible/vars/cluster_vars"
  print(path)
  clusters = next(walk(path))[1]
  t = PrettyTable(['Cluster Name'])
  t.align = "l"

  for c in clusters:
    t.add_row([c])

  print t

def cluster_provision(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Invoking Ansible and streaming its output ..." + bcolors.ENDC)
  invoke_ansible(arg_vars, project_root, arg_vars['cluster_id'] + ".yml")
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible." + bcolors.ENDC)
