#!/usr/bin/env python

class bcolors:
    HEADER = '\033[90m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_fail(x):
  base = "{0}> {1}{2}"
  print(base.format(bcolors.FAIL, x, bcolors.ENDC))

def print_done(x):
  base = "{0}{1}> {2}{3}"
  print(base.format(bcolors.OKBLUE, bcolors.BOLD, x, bcolors.ENDC))

def print_ok(x):
  base = "{0}> {1}{2}"
  print(base.format(bcolors.OKBLUE, x, bcolors.ENDC))

def print_ok_pending(x):
  base = "{0}> {1} ...{2}"
  print(base.format(bcolors.OKBLUE, x, bcolors.ENDC))

