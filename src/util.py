#!/usr/bin/env python

from os.path import exists
from colors import bcolors, print_fail
from mako.template import Template

def provisioning_playbook(cluster_id):
  base = "{0}.yml"
  return base.format(cluster_id)

def post_provisioning_playbook(cluster_id):
  base = "{0}_post.yml"
  return base.format(cluster_id)

def cluster_remove_playbook():
  return "cluster_remove.yml"

def machine_profiles_path(project_root, cluster_id):
  base = "{0}/ansible/vars/cluster_vars/{1}/machine_profiles"
  return base.format(project_root, cluster_id)

def cluster_path(project_root, cluster_id):
  base = "{0}/ansible/vars/cluster_vars/{1}"
  return base.format(project_root, cluster_id)

def machine_profile_file(project_root, cluster_id, profile_id):
  base = "{0}/{2}_profile.yml"
  profiles_path = machine_profiles_path(project_root, cluster_id)
  return base.format(profiles_path, profile_id)

def cluster_file(project_root, cluster_id):
  base = "{0}/ansible/group_vars/${1}.yml"
  return base.format(project_root, cluster_id)

def machines_remove_file(project_root):
  base = "{0}/ansible/machines_remove.yml"
  return base.format(project_root)

def cluster_remove_file(project_root):
  base = "{0}/ansible/cluster_remove.yml"
  return base.format(project_root)

def user_post_playbook_file(project_root, cluster_id):
  base = "{0}/ansible/{1}_post.yml"
  return base.format(project_root, cluster_id)

def profile_template():
  base = "ansible_template/vars/cluster_vars/machine_profiles/profile_template.yml"
  return Template(resource_string(__name__, base))

def default_profile_template():
  base = "ansible_template/vars/cluster_vars/machine_profiles/default_profile.yml"
  return Template(resource_string(__name__, base))

def common_cluster_template():
  base = "ansible_template/group_vars/all.yml"
  return Template(resource_string(__name__, base))

def machines_remove_template():
  base = "ansible_template/machines_remove.yml"
  return Template(resource_string(__name__, base))

def cluster_remove_template():
  base = "ansible_template/cluster_remove.yml"
  return Template(resource_string(__name__, base))

def user_post_playbook_template():
  base = "ansible_template/engraver_post.yml"
  return Template(resource_filename(__name__, base))

def verify_cluster_exists(arg_vars, project_root):
  cluster_id = arg_vars['cluster_id']
  f = cluster_file(project_root, cluster_id)
  r = exists(f)

  if not r:
    print_fail("Cluster {0} does not exist.".format(cluster_id))
  return r

def verify_profile_exists(arg_vars, project_root):
  cluster_id = arg_vars['cluster_id']
  profile_id = arg_vars['profile_id']
  f = machines_profile_file(project_root, cluster_id, profile_id)
  r = exists(f)

  if not r:
    print_fail("Profile {0} does not exist".format(profile_id))
  return r
