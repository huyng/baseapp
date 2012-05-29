#!/usr/bin/env python
# bootstrap.py
# Bootstrap and setup a virtualenv with the specified requirements.txt
import sys
import subprocess as SP
import os.path as P

from optparse import OptionParser

FILE_PATH     = P.dirname(P.abspath(__file__))
REQUIREMENTS  = P.join(FILE_PATH, 'deps/requirements.txt')
ENVROOT       = P.join(FILE_PATH, 'env')
ACTIVATE_THIS = P.join(ENVROOT, 'bin/activate_this.py')
ACTIVATE_SH   = P.join(ENVROOT, 'bin/activate')
VIRTUALENV    = "virtualenv"

usage       = """usage: %prog [options]"""
description = """creates a virtualenvironment to run your applications"""
parser      = OptionParser(usage=usage, description=description)

parser.add_option("-c", "--clear",
                  dest="clear",
                  action="store_true",
                  help="clear out existing virtualenv")

parser.add_option("-m", "--mixed",
                  dest="mixed",
                  action="store_true",
                  help="When creating a new virtual environment, use a mixture of site-packages in global environment AND in the local virtual environment. (Not recommended)")

def main():
    # create virtualenv if it doesn't exist
    if not P.exists(ACTIVATE_THIS) and not options.mixed:
        print('Creating CLEAN virtual environment\n')
        SP.call(['mkdir', '-p', ENVROOT])
        SP.call([VIRTUALENV, ENVROOT, "--no-site-packages"])
        
    elif not P.exists(ACTIVATE_THIS) and options.mixed:
        print('Creating MIXED virtual environment\n')
        SP.call(['mkdir', '-p', ENVROOT])
        SP.call([VIRTUALENV, ENVROOT])
        
    elif P.exists(ACTIVATE_THIS) and options.mixed:
        print('Warning: the --mixed option should only be applied when starting new virtualenvs. It has no effect on existing environments')

    if options.clear:
        SP.call([VIRTUALENV, "--clear", "--distribute", ENVROOT])
    
    execfile(ACTIVATE_THIS, dict(__file__=ACTIVATE_THIS))
    PIP = P.join(ENVROOT, 'bin/pip')
    
    # parse requirements file
    for line in open(REQUIREMENTS, "r"):
        
        # ignore emptylines
        if not line.strip():
            continue
        
        # ignore comments
        elif line.strip().startswith('#'):
            continue
        
        # run shell script called run.sh
        elif line.strip().startswith(":sh"):
            tokens = line.split(' ')
            if len(tokens) > 1:
                build_dir = tokens[-1].strip()
                print "cd %s && bash run.sh -" % build_dir
                SP.call("cd %s && VIRTUAL_ENV='%s' bash run.sh" % (build_dir, ENVROOT), shell=True)
        
        # source installation (make && make install)
        elif line.strip().startswith(':makeinstall'):
            tokens = line.split(' ')
            if len(tokens) > 1:
                build_dir = tokens[-1].strip()
                print "cd %s && make && make install && cd -" % build_dir
                SP.call("cd %s && make && make install && cd -" % build_dir, shell=True)
        
        # pip install
        else:
            print "%s install %s" % (PIP, line)
            SP.call("%s install %s" % (PIP, line), shell=True)


if __name__ == "__main__":
    options, pos_args = parser.parse_args()
    main()
    sys.exit(0)
