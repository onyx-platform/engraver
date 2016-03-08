#!/usr/bin/env python

import json
import yaml
import ConfigParser

from pkg_resources import resource_filename, resource_string
from prettytable import PrettyTable
from mako.template import Template
from os.path import isfile, join, expanduser, exists
from os import listdir, walk
from subprocess import call

from colors import bcolors
from util import verify_cluster_exists, verify_profile_exists
from ansible import invoke_ansible, refresh_provisioning_playbook

def machines_describe(arg_vars, project_root):
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  if exists(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    t = PrettyTable(['Profile ID', 'Size', 'Services', 'Desired Count'])
    t.align = "l"
    t.align["Desired Count"] = "c"
    for f in files:
      with open(path + "/" + f, 'r') as stream:
        content = yaml.load(stream)
        t.add_row([content['profile_id'], content['ec2_instance_type'],
                   ", ".join(content['machine_services']),
                   content['n_machine_instances']])
    print t
  else:
    print(bcolors.OKBLUE + "> No machine profiles were found. " + bcolors.ENDC)

def machines_teardown(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Removing machines provisioned with profile id " + arg_vars['profile_id'] + " ..." + bcolors.ENDC)
  f = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles/" + arg_vars['profile_id'] + "_profile.yml"

  if verify_profile_exists(arg_vars, project_root):
    with open(f, "r") as stream:
      content = yaml.load(stream)
      content['n_machine_instances'] = 0

    with open(f, "w") as stream:
      stream.write(yaml.dump(content))

    tpl = Template(resource_string(__name__, "ansible_template/machines_remove.yml"))
    with open(project_root + "/ansible/machines_remove.yml", "w") as text_file:
      text_file.write(tpl.render(profile=arg_vars['profile_id']))

    print(bcolors.OKBLUE + "> Scaling down instances. Streaming Ansible output ... " + bcolors.ENDC)
    invoke_ansible(arg_vars, project_root, "machines_remove.yml")
    call(["rm", f])
    print(bcolors.OKBLUE + bcolors.BOLD + "> Finished scale down." + bcolors.ENDC)

def machines_list(arg_vars, project_root, hint=True):
  if hint:
    print(bcolors.OKBLUE + "> Hint: Displaying cached contents. Refresh status with: engraver machines cache" + bcolors.ENDC)
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
    print(bcolors.FAIL + "> No cached contents found." + bcolors.ENDC)

def machines_cache(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Updating local cache of cluster machines. Streaming Ansible output ..." + bcolors.ENDC)

  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)

  aws_key_name = config.get('aws', 'aws_key_name', 0)
  pem_file_path = config.get('aws', 'pem_file_name', 0)

  if(verify_cluster_exists(arg_vars, project_root)):
    invoke_ansible(arg_vars, project_root, "refresh_cache.yml")
    print(bcolors.OKBLUE + bcolors.BOLD + "> Finished updating local cache. Displaying cluster: " + bcolors.ENDC)
    machines_list(arg_vars, project_root, hint=False)

def machines_scale(arg_vars, project_root):
  f = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles/" + arg_vars['profile_id'] + "_profile.yml"
  with open(f, "r") as stream:
    content = yaml.load(stream)
    content['n_machine_instances'] = int(arg_vars['n'])

  with open(f, "w") as stream:
    stream.write(yaml.dump(content))

  print(bcolors.OKBLUE + bcolors.BOLD + "> Updated local Ansible playbook. Now run: engraver cluster provision" + bcolors.ENDC)

def machines_new(arg_vars, project_root):
  print(bcolors.OKBLUE + "> Creating new Ansible machine profile..." + bcolors.ENDC)
  tpl = Template(resource_string(__name__, "ansible_template/vars/cluster_vars/machine_profiles/profile_template.yml"))

  with open(project_root +
            ("/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] +
             "/machine_profiles/" + arg_vars['profile_id'] +
             "_profile.yml"), "w") as text_file:
    text_file.write(tpl.render(profile_id=arg_vars['profile_id'],
                               n_instances=arg_vars['n'],
                               size=arg_vars['size'],
                               services=[x.strip() for x in arg_vars['services'].split(",")]))

  refresh_provisioning_playbook(arg_vars, project_root)

  print(bcolors.OKBLUE + bcolors.BOLD + "> Finished Ansible machine profile creation." + bcolors.ENDC)
