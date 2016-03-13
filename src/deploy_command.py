#!/usr/bin/env python

import json
import os

from subprocess import check_output, call

from ansible import invoke_ansible, refresh_deployment_playbook
from colors import bcolors, print_ok, print_ok_pending, print_done

def deploy(arg_vars, project_root):
  organization = arg_vars['dockerhub_username']
  version = check_output(["lein", "project-version"]).strip()
  project_name = os.path.relpath(project_root, "..")
  image = organization + "/" + project_name + ":" + version

  if not arg_vars.get('skip_uberjar'):
    print_ok_pending("Creating an uberjar for your project. Streaming Leiningen output")
    call(["lein", "uberjar"])
    print_done("Finished creating the uberjar.")
    print("")

  print_ok_pending("Creating a container. Streaming Docker output")
  call(["docker", "build", "-t", image, project_root])
  print_done("Finished building container image " + image + ".")
  print("")

  print_ok_pending("Uploading image to DockerHub")
  call(["docker", "push", image])
  print_done("Finished pushing image.")
  print("")

  print_ok_pending("Updating Ansible deployment playbook")
  refresh_deployment_playbook(arg_vars, project_root)
  print_done("Ansible playbook update complete.")
  print("")

  print_ok_pending("Running Ansible deployment playbook. Streaming Ansible output")
  invoke_ansible(arg_vars, project_root, "deploy.yml",
                 {"onyx_docker_image": image,
                  "onyx_tenancy_id": arg_vars['tenancy_id'],
                  "onyx_n_peers": arg_vars['n_peers']})
  print_done("Finished running Ansible. Onyx has been successfully deployed.")
