#!/usr/bin/env python

import yaml
import util

from prettytable import PrettyTable
from mako.template import Template
from os.path import isfile, join
from os import listdir, walk
from subprocess import call
from colors import bcolors, print_ok_pending, print_ok, print_fail, print_done
from aws import default_amis, default_azs

from machines_command import machines_teardown
from ansible import invoke_ansible, refresh_provisioning_playbook

def cluster_new(arg_vars, project_root):
  print_ok_pending("Creating default Ansible playbook")

  cluster_id = arg_vars['cluster_id']
  call(["mkdir", "-p", util.machine_profiles_path(project_root, cluster_id)])

  tpl = util.default_profile_template()
  f = util.machine_profile_file(project_root, cluster_id, "default")
  region = arg_vars.get('aws_region', 'us-east-1')
  ami = default_amis[region]
  az = arg_vars.get('aws_az') or default_azs[region]

  with open(f, "w") as handle:
    handle.write(tpl.render(ami = ami))

  tpl = util.common_cluster_template()
  f = util.cluster_file(project_root, cluster_id)
  with open(f, "w") as text_file:
    text_file.write(tpl.render(cluster_id = cluster_id,
                               aws_region = region,
                               aws_az = az))

  refresh_provisioning_playbook(arg_vars, project_root)

  tpl = util.user_post_playbook_template()
  f = util.user_post_playbook_file(project_root, cluster_id)
  with open(f, "w") as handle:
    handle.write(tpl.render())

  print_done("Finished Ansible playbook creation.")
  print("")

def cluster_describe(arg_vars, project_root):
  path = project_root + "/ansible/vars/cluster_vars"
  clusters = next(walk(path))[1]
  t = PrettyTable(['Cluster Name', 'Cloud Provider', 'Region', 'Availability Zone'])
  t.align = "l"

  for c in clusters:
    with open(util.cluster_file(project_root, c), "r") as stream:
      content = yaml.load(stream)
      region = content['aws_region']
      az = content['aws_subnet_az']
      t.add_row([c, 'AWS', region, az])

  print t

def cluster_teardown(arg_vars, project_root):
  print_ok_pending("Tearing down all machine profiles")
  print("")

  cluster_id = arg_vars['cluster_id']
  path = util.machine_profiles_path(project_root, cluster_id)
  files = [f for f in listdir(path) if isfile(join(path, f))]

  for f in files:
    with open(path + "/" + f, 'r') as stream:
      content = yaml.load(stream)
      arg_vars['profile_id'] = content['profile_id']
      machines_teardown(arg_vars, project_root)

  print_ok_pending("Tearign down the VPC")

  tpl = util.cluster_remove_template()
  with open(util.cluster_remove_file(project_root), "w") as text_file:
    path = project_root + "/ansible/roles"
    services = next(walk(path))[1]
    text_file.write(tpl.render(services=services))

  invoke_ansible(arg_vars, project_root, util.cluster_remove_playbook())

  call(["rm", util.cluster_file(project_root, cluster_id)])
  call(["rm", "-r", util.cluster_path(project_root, cluster_id)])

  print_done("Finished running Ansible.")

def cluster_provision(arg_vars, project_root):
  print_ok_pending("Invoking Ansible and streaming its output")

  cluster_id = arg_vars['cluster_id']

  refresh_provisioning_playbook(arg_vars, project_root)
  invoke_ansible(arg_vars, project_root, util.provisioning_playbook(cluster_id))
  invoke_ansible(arg_vars, project_root, util.post_provisioning_playbook(cluster_id))

  print_done("Finished running Ansible.")
