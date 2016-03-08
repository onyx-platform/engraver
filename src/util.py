#!/usr/bin/env python

from os.path import exists
from colors import bcolors

def verify_cluster_exists(arg_vars, project_root):
  if not exists(project_root + "/ansible/group_vars/" + arg_vars['cluster_id'] + ".yml"):
    print(bcolors.FAIL + "> Cluster " + arg_vars['cluster_id'] + " does not exist. " + bcolors.ENDC)
    return False
  else:
    return True

def verify_profile_exists(arg_vars, project_root):
  f = project_root + "/ansible/vars/cluster_vars/" + arg_vars['cluster_id'] + "/machine_profiles/" + arg_vars['profile_id'] + "_profile.yml"
  if not exists(f):
    print(bcolors.FAIL + "> Profile " + arg_vars['profile_id'] + " does not exist. " + bcolors.ENDC)
    return False
  else:
    return True
