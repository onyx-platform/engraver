#!/usr/bin/env python

import yaml

from pkg_resources import resource_filename, resource_string
from prettytable import PrettyTable
from mako.template import Template
from os.path import isfile, join
from os import listdir, walk
from subprocess import call
from colors import bcolors

def cluster_new(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Creating default Ansible machine profile..." + bcolors.ENDC)
  default_profile_file = resource_filename(__name__, "ansible_template/cluster_vars/machine_profiles/default_profile.yml")
  call(["mkdir", "-p", (project_root + "/ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles")])
  call(["cp", default_profile_file, project_root + "/ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles/default_profile.yml"])

  tpl = Template(resource_string(__name__, "ansible_template/group_vars/all.yml"))

  with open((project_root + "/ansible/group_vars/" + arg_vars['cluster_name'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(cluster_name=arg_vars['cluster_name']))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible default machine profile creation." + bcolors.ENDC)
  print("")

def cluster_describe(arg_vars, project_root):
  path = project_root + "/ansible/cluster_vars"
  print(path)
  clusters = next(walk(path))[1]
  t = PrettyTable(['Cluster Name'])
  t.align = "l"

  for c in clusters:
    t.add_row([c])

  print t

def cluster_machines_describe(arg_vars, project_root):
  path = project_root + "/ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles"
  files = [f for f in listdir(path) if isfile(join(path, f))]
  t = PrettyTable(['Profile ID', 'N Instances', 'Services'])
  t.align["Profile ID"] = "l"
  t.align["Services"] = "l"
  for f in files:
    with open(path + "/" + f, 'r') as stream:
      content = yaml.load(stream)
      t.add_row([content['profile_id'], content['n_machine_instances'], ", ".join(content['machine_services'])])
  print t

def cluster_machines_new(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Creating new Ansible machine profile..." + bcolors.ENDC)
  tpl = Template(resource_string(__name__, "ansible_template/cluster_vars/machine_profiles/profile_template.yml"))

  with open(project_root +
            ("/ansible/cluster_vars/" + arg_vars['cluster_name'] +
             "/machine_profiles/" + arg_vars['profile_id'] +
             "_profile.yml"), "w") as text_file:
    text_file.write(tpl.render(profile_id=arg_vars['profile_id'],
                               n_instances=arg_vars['n'],
                               services=[x.strip() for x in arg_vars['services'].split(",")]))

  tpl = Template(resource_string(__name__, "ansible_template/engraver_playbook.yml"))
  path = project_root + "/ansible/cluster_vars/" + arg_vars['cluster_name'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]
  with open((project_root + "/ansible/engraver_playbook.yml"), "w") as text_file:
    text_file.write(tpl.render(profiles=profile_files))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible machine profile creation." + bcolors.ENDC)

def cluster_provision(arg_vars, project_root):
  config = ConfigParser.ConfigParser()
  config.read('.engraver_profile')

  aws_key_name = config['aws']['aws_key_name']
  pem_file_path = config['aws']['pem_file_name']

  call(["ansible-playbook", "--private-key", pem_file_path,
        "-i", ",", "-e", "remote_user='ubuntu'",
        "-e", ("aws_key_name=" + aws_key_name),
        project_root + "/ansible/engraver_playbook.yml"])
