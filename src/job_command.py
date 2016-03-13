#!/usr/bin/env python

from colors import bcolors, print_ok_pending, print_done
from subprocess import call
import util

from ansible import refresh_submit_playbook, refresh_kill_playbook, invoke_ansible

def job_submit(arg_vars, project_root):
  print_ok_pending("Invoking Ansible and streaming its output")

  refresh_submit_playbook(arg_vars, project_root)
  invoke_ansible(arg_vars, project_root,
                 util.job_submit_playbook(),
                 {"onyx_job_name": arg_vars['job_name']})

  print_done("Finished running Ansible.")

def job_kill(arg_vars, project_root):
  print_ok_pending("Invoking Ansible and streaming its output")

  refresh_kill_playbook(arg_vars, project_root)
  invoke_ansible(arg_vars, project_root,
                 util.job_kill_playbook(),
                 {"onyx_job_id" : arg_vars['job_id']})

  print_done("Finished running Ansible.")
