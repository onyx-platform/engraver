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

from ansible import invoke_ansible

def refresh_playbook(arg_vars, project_root):
  tpl = Template(resource_string(__name__, "ansible_template/engraver_aws.yml"))
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]

  profiles = {}
  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      profiles[content['profile_id']] = {'machine_services': content['machine_services']}

  with open((project_root + "/ansible/" + arg_vars['cluster_id'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(profiles=profiles))

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

def cluster_machines_describe(arg_vars, project_root):
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  files = [f for f in listdir(path) if isfile(join(path, f))]
  t = PrettyTable(['Profile ID', 'Desired Count', 'Services'])
  t.align["Profile ID"] = "l"
  t.align["Services"] = "l"
  for f in files:
    with open(path + "/" + f, 'r') as stream:
      content = yaml.load(stream)
      t.add_row([content['profile_id'], content['n_machine_instances'], ", ".join(content['machine_services'])])
  print t

def cluster_machines_list(arg_vars, project_root, hint=True):
  if hint:
    print(bcolors.OKBLUE + "> Hint: Displaying cached contents. Refresh status with: engraver cluster machines cache" + bcolors.ENDC)
    print("")
  path = project_root + "/.engraver/clusters/" + arg_vars['cluster_id'] + ".json"

  if exists(path):
    t = PrettyTable(['', 'ID', 'Profile', 'Public DNS Name', 'Private IP'])
    t.align = "l"
    contents = open(path, 'r').read()
    machines = sorted(json.loads(contents), key=lambda k: k.get('tags').get('ProfileId'))
    for index, m in enumerate(machines):
        t.add_row([index + 1, m.get('id'), m.get('tags').get('ProfileId'), m.get('public_dns_name'), m.get('private_ip_address')])
    print t
  else:
    print(bcolors.OKBLUE + "> No cached contents found." + bcolors.ENDC)

def cluster_machines_cache(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Updating local cache of cluster machines. Streaming Ansible output ..." + bcolors.ENDC)

  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)

  aws_key_name = config.get('aws', 'aws_key_name', 0)
  pem_file_path = config.get('aws', 'pem_file_name', 0)

  chdir(project_root + "/ansible")
  invoke_ansible(arg_vars, project_root, "refresh_cache.yml")

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished updating local cache. Displaying cluster: " + bcolors.ENDC)
  cluster_machines_list(arg_vars, project_root, hint=False)

def cluster_machines_scale(arg_vars, project_root):
  f = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles/" + arg_vars['profile_id'] + "_profile.yml"
  with open(f, "r") as stream:
    content = yaml.load(stream)
    content['n_machine_instances'] = int(arg_vars['n'])

  with open(f, "w") as stream:
    stream.write(yaml.dump(content))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Updated local Ansible playbook. Now run: engraver cluster provision" + bcolors.ENDC)

def cluster_machines_new(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Creating new Ansible machine profile..." + bcolors.ENDC)
  tpl = Template(resource_string(__name__, "ansible_template/vars/cluster_vars/machine_profiles/profile_template.yml"))

  with open(project_root +
            ("/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] +
             "/machine_profiles/" + arg_vars['profile_id'] +
             "_profile.yml"), "w") as text_file:
    text_file.write(tpl.render(profile_id=arg_vars['profile_id'],
                               n_instances=arg_vars['n'],
                               services=[x.strip() for x in arg_vars['services'].split(",")]))

  refresh_playbook(arg_vars, project_root)

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible machine profile creation." + bcolors.ENDC)

def cluster_provision(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Invoking Ansible and streaming its output ..." + bcolors.ENDC)
  invoke_ansible(arg_vars, project_root, arg_vars['cluster_id'] + ".yml")
  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished running Ansible." + bcolors.ENDC)
