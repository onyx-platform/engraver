#!/usr/bin/env python

import ConfigParser
import shlex
import yaml

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
  tpl = Template(resource_string(__name__, "ansible_template/engraver_aws.yml"))
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]

  services = {}
  service_graph = {}
  profiles = []
  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      profiles.append(content['profile_id'])
      for s in content['machine_services']:
        rets = services.get(s, [])
        rets.append(content['profile_id'])
        services[s] = rets

  for s in services.keys():
    with open((project_root + "/ansible/roles/" + s + "/defaults/main.yml"), "r") as text_file:
      content = yaml.load(text_file)
      service_graph[s] = set(content.get('service_dependencies', {}))

  service_seq = toposort_flatten(service_graph)
  with open((project_root + "/ansible/" + arg_vars['cluster_id'] + ".yml"), "w") as text_file:
    text_file.write(tpl.render(cluster_id=arg_vars['cluster_id'],
                               services=services,
                               profiles=profiles,
                               service_seq=service_seq,
                               service_graph=service_graph))

def refresh_deployment_playbook(arg_vars, project_root):
  tpl = Template(resource_string(__name__, "ansible_template/deploy.yml"))
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]

  profiles = []
  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      if 'onyx' in content['machine_services']:
        profiles.append(content['profile_id'])

  with open((project_root + "/ansible/deploy.yml"), "w") as text_file:
    text_file.write(tpl.render(profiles=profiles))

def refresh_submit_playbook(arg_vars, project_root):
  tpl = Template(resource_string(__name__, "ansible_template/job_submit.yml"))
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]

  profiles = []
  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      if 'onyx' in content['machine_services']:
        profiles.append(content['profile_id'])

  with open((project_root + "/ansible/job_submit.yml"), "w") as text_file:
    text_file.write(tpl.render(profiles=profiles))

def refresh_kill_playbook(arg_vars, project_root):
  tpl = Template(resource_string(__name__, "ansible_template/job_kill.yml"))
  path = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles"
  profile_files = [f for f in listdir(path) if isfile(join(path, f))]

  profiles = []
  for f in profile_files:
    with open((path + "/"  + f), "r") as handle:
      content = yaml.load(handle)
      if 'onyx' in content['machine_services']:
        profiles.append(content['profile_id'])

  with open((project_root + "/ansible/job_kill.yml"), "w") as text_file:
    text_file.write(tpl.render(profiles=profiles))
