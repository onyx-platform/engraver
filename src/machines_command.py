#!/usr/bin/env python

import json
import yaml
import ConfigParser
import util

from pkg_resources import resource_filename, resource_string
from prettytable import PrettyTable
from os.path import isfile, join, expanduser, exists
from os import listdir
from subprocess import call

from colors import bcolors, print_ok, print_done, print_fail, print_ok_pending
from util import verify_cluster_exists, verify_profile_exists
from ansible import invoke_ansible, refresh_provisioning_playbook
from aws import default_amis

def machines_describe(arg_vars, project_root):
  cluster_id = arg_vars['cluster_id']
  path = util.machine_profiles_path(project_root, cluster_id)

  if exists(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    t = PrettyTable(['Profile ID', 'Size', 'Services', 'Desired Count'])
    t.align = "l"
    t.align["Desired Count"] = "c"
    for f in files:
      with open(path + "/" + f, 'r') as stream:
        content = yaml.load(stream)
        t.add_row([content['profile_id'],
                   content['ec2_instance_type'],
                   ", ".join(content.get('machine_services', [])),
                   content['n_machine_instances']])
    print t
  else:
    print_fail("No machine profiles were found for this cluster.")

def machines_teardown(arg_vars, project_root):
  cluster_id = arg_vars['cluster_id']
  profile_id = arg_vars['profile_id']
  f = util.machine_profile_file(project_root, cluster_id, profile_id)

  print_ok_pending("Removing machines provisioned with profile id " + profile_id)

  if verify_profile_exists(arg_vars, project_root):
    with open(f, "r") as stream:
      content = yaml.load(stream)
      content['n_machine_instances'] = 0

    with open(f, "w") as stream:
      stream.write(yaml.dump(content))

    tpl = util.machines_remove_template()
    with open(util.machines_remove_file(project_root), "w") as handle:
      handle.write(tpl.render(profile = profile_id))

    print_ok_pending("Scaling down instances. Streaming Ansible output")
    invoke_ansible(arg_vars, project_root, "machines_remove.yml")
    call(["rm", f])
    print(bcolors.OKBLUE + bcolors.BOLD + "> Finished scale down." + bcolors.ENDC)

def machines_list(arg_vars, project_root, hint=True):
  if hint:
    print_ok("Hint: Displaying cached contents. Refresh status with: engraver machines cache")
    print("")

  path = project_root + "/.engraver/clusters/" + arg_vars['cluster_id'] + ".json"
  if exists(path):
    t = PrettyTable(['', 'ID', 'Profile', 'Public DNS Name', 'Private IP'])
    t.align = "l"
    contents = open(path, 'r').read()
    machines = sorted(json.loads(contents), key=lambda k: k.get('tags').get('ProfileId'))
    for index, m in enumerate(machines):
        t.add_row([index + 1,
                   m.get('id'),
                   m.get('tags').get('ProfileId'),
                   m.get('public_dns_name'),
                   m.get('private_ip_address')])
    print t
  else:
    print_fail("No cached contents found.")

def machines_cache(arg_vars, project_root):
  print_ok_pending("Updating local cache of cluster machines. Streaming Ansible output")

  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)

  aws_key_name = config.get('aws', 'aws_key_name', 0)
  pem_file_path = config.get('aws', 'pem_file_name', 0)

  if(verify_cluster_exists(arg_vars, project_root)):
    invoke_ansible(arg_vars, project_root, util.refresh_cache_playbook())
    print_done("Finished updating local cache. Displaying cluster: ")
    machines_list(arg_vars, project_root, hint=False)

def machines_scale(arg_vars, project_root):
  cluster_id = arg_vars['cluster_id']
  profile_id = arg_vars['profile_id']
  f = util.machine_profile_file(project_root, cluster_id, profile_id)

  with open(f, "r") as stream:
    content = yaml.load(stream)
    content['n_machine_instances'] = int(arg_vars['n'])

  with open(f, "w") as stream:
    stream.write(yaml.dump(content))

  print_done("Updated local Ansible playbook. Now run: engraver cluster provision")

def machines_new(arg_vars, project_root):
  print_ok_pending("Creating new Ansible machine profile")

  cluster_id = arg_vars['cluster_id']
  profile_id = arg_vars['profile_id']
  tpl = util.profile_template()
  path = util.machine_profile_file(project_root, cluster_id, profile_id)

  cf = util.cluster_file(project_root, cluster_id)
  contents = yaml.load(open(cf, 'r').read())
  region = contents['aws_region']
  ami = default_amis[region]

  with open(path, "w") as handle:
    if (arg_vars.get('services')):
      services = [x.strip() for x in arg_vars.get('services').split(",")]
    else:
      services = []
    handle.write(tpl.render(profile_id = arg_vars['profile_id'],
                            n_instances = arg_vars['n'],
                            size = arg_vars['size'],
                            ami = ami,
                            services = services))

  refresh_provisioning_playbook(arg_vars, project_root)
  print_done("Finished Ansible machine profile creation")
