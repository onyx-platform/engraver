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

from machines_command import machines_teardown
from ansible import invoke_ansible, refresh_provisioning_playbook

def cluster_new(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Creating default Ansible playbook..." + bcolors.ENDC)
  default_profile_file = resource_filename(__name__, "ansible_template/vars/cluster_vars/machine_profiles/default_profile.yml")
  call(["mkdir", "-p", (project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles")])
  call(["cp", default_profile_file, project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles/default_profile.yml"])

  tpl = Template(resource_string(__name__, "ansible_template/group_vars/all.yml"))

  with open((project_root + "/ansible/group_vars/" + arg_vars['cluster_id'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(cluster_id=arg_vars['cluster_id'],
                               aws_region=arg_vars['aws_region'],
                               aws_az=arg_vars['aws_az']))

  refresh_provisioning_playbook(arg_vars, project_root)

  post_file = resource_filename(__name__, "ansible_template/engraver_post.yml")
  call(["cp", post_file, (project_root + "/ansible/" + arg_vars['cluster_id'] + "_post.yml")])

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible playbook creation." + bcolors.ENDC)
  print("")

def cluster_describe(arg_vars, project_root):
  path = project_root + "/ansible/vars/cluster_vars"
  clusters = next(walk(path))[1]
  t = PrettyTable(['Cluster Name', 'Cloud Provider', 'Region', 'Availability Zone'])
  t.align = "l"

  for c in clusters:
    with open((project_root + "/ansible/group_vars/" + c + ".yml"), "r") as stream:
      content = yaml.load(stream)
      region = content['aws_region']
      az = content['aws_subnet_az']
      t.add_row([c, 'AWS', region, az])

  print t

def cluster_teardown(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Tearing down all machine profiles ... " + bcolors.ENDC)
  print("")

  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  files = [f for f in listdir(path) if isfile(join(path, f))]

  for f in files:
    with open(path + "/" + f, 'r') as stream:
      content = yaml.load(stream)
      arg_vars['profile_id'] = content['profile_id']
      machines_teardown(arg_vars, project_root)

  print(bcolors.OKBLUE + "> Tearing down the VPC ... " + bcolors.ENDC)

  tpl = Template(resource_string(__name__, "ansible_template/cluster_remove.yml"))
  with open(project_root + "/ansible/cluster_remove.yml", "w") as text_file:
    path = project_root + "/ansible/roles"
    services = next(walk(path))[1]
    text_file.write(tpl.render(services=services))

  invoke_ansible(arg_vars, project_root, "cluster_remove.yml")
  call(["rm", (project_root + "/ansible/group_vars/" + arg_vars['cluster_id'] + ".yml")])
  call(["rm", "-r", (project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'])])
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible." + bcolors.ENDC)

def cluster_provision(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Invoking Ansible and streaming its output ..." + bcolors.ENDC)
  refresh_provisioning_playbook(arg_vars, project_root)
  invoke_ansible(arg_vars, project_root, arg_vars['cluster_id'] + ".yml")
  invoke_ansible(arg_vars, project_root, arg_vars['cluster_id'] + "_post.yml")
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible." + bcolors.ENDC)
