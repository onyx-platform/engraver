#!/usr/bin/env python

import ConfigParser
import shlex
import yaml
import util

from pkg_resources import resource_string
from mako.template import Template
from os.path import isfile, join, expanduser, exists
from os import chdir, listdir
from subprocess import call
from toposort import toposort_flatten

def form_env_vars(extras):
  result = []
  for k, v in extras.iteritems():
    result.append("-e")
    result.append(k + "=" + v)
  return result

def invoke_ansible(arg_vars, project_root, playbook, extras = {}):
  config = ConfigParser.ConfigParser()
  engraver_profile = expanduser("~") + "/.engraver"
  config.read(engraver_profile)

  aws_access_key = config.get('aws', 'aws_access_key', 0)
  aws_secret_key = config.get('aws', 'aws_secret_key', 0)
  aws_key_name = config.get('aws', 'aws_key_name', 0)
  pem_file_path = config.get('aws', 'pem_file_name', 0)
  remote_user = config.get('aws', 'remote_user', 0)

  chdir(project_root + "/ansible")

  pre = ["ansible-playbook", "--private-key", pem_file_path,
         "-i", ",",
         "-e", ("remote_user=" + remote_user),
         "-e", ("onyx_cluster_id=" + arg_vars['cluster_id']),
         "-e", ("aws_key_name=" + aws_key_name),
         "-e", ("aws_access_key=" + aws_access_key),
         "-e", ("aws_secret_key=" + aws_secret_key),
         "-e", ("engraver_root=" + project_root)]

  raw = shlex.split(arg_vars.get('ansible') or "")
  post = [project_root + "/ansible/" + playbook]
  call(pre + raw + form_env_vars(extras) + post)

def refresh_provisioning_playbook(arg_vars, project_root):
  cluster_id = arg_vars['cluster_id']
  tpl = util.provisioning_template()
  path = util.machine_profiles_path(project_root, cluster_id)
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]

  services = {}
  service_graph = {}
  profiles = []
  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      profiles.append(content['profile_id'])
      for s in content.get('machine_services', []):
        rets = services.get(s, [])
        rets.append(content['profile_id'])
        services[s] = rets

  for s in services.keys():
    with open((project_root + "/ansible/roles/" + s + "/defaults/main.yml"), "r") as text_file:
      content = yaml.load(text_file)
      service_graph[s] = set(content.get('service_dependencies', {}))

  service_seq = toposort_flatten(service_graph)
  with open(util.provisioning_file(project_root, cluster_id), "w") as text_file:
    text_file.write(tpl.render(cluster_id = cluster_id,
                               services = services,
                               profiles = profiles,
                               service_seq = service_seq,
                               service_graph = service_graph))

def collect_onyx_profiles(project_root, arg_vars):
  cluster_id = arg_vars['cluster_id']
  path = util.machine_profiles_path(project_root, cluster_id)
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]
  profiles = []

  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      if 'onyx' in content.get('machine_services', []):
        profiles.append(content['profile_id'])

  return profiles

def refresh_deployment_playbook(arg_vars, project_root):
  tpl = util.deploy_template()
  profiles = collect_onyx_profiles(project_root, arg_vars)

  with open(util.deploy_file(project_root), "w") as text_file:
    text_file.write(tpl.render(profiles = profiles))

def refresh_submit_playbook(arg_vars, project_root):
  tpl = util.job_submit_template()
  profiles = collect_onyx_profiles(project_root, arg_vars)

  with open(util.job_submit_file(project_root), "w") as handle:
    handle.write(tpl.render(profiles=profiles))

def refresh_kill_playbook(arg_vars, project_root):
  tpl = util.job_kill_template()
  profiles = collect_onyx_profiles(project_root, arg_vars)

  with open(util.job_kill_file(project_root), "w") as handle:
    handle.write(tpl.render(profiles=profiles))
