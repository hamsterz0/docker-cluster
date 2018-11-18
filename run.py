import argparse
import sys
import json
import pdb
import os
import shutil
from distutils.dir_util import copy_tree


def get_frameworks(config, processing):
    frameworks = []
    for framework in processing:
        if framework in config['processing']:
            frameworks.append(config['processing'][framework]['name'])
    return frameworks

def create_image_name(frameworks):
    name = [framework for framework in frameworks]
    name.append('base')
    # TODO: For now the name is just the framework name, later we can add more. 
    return '-'.join(name)

def create_docker_file(frameworks, dep): 
    def create_docker_file_helper(framework, dep, files):
        for dependencies in framework:
            files.append(dep[dependencies]['install'])

    base_dockerfile = dep['base']['install']
    files = [base_dockerfile]
    # install dependencies first. 
    for framework in frameworks:
        if 'dep' in dep[framework]:
            create_docker_file_helper(dep[framework]['dep'], dep, files) 

    # install the processing frameworks now
    for framework in frameworks:
        files.append(dep[framework]['install'])

    with open('config/Dockerfile', 'w') as outfile:
        for fname in files:
            with open(fname) as f:
                for line in f:
                    outfile.write(line)


def create_image(frameworks):
    dep = json.load(open('dependencies.json'))
    create_docker_file(frameworks, dep)
    # create a image dir
    os.mkdir('./image')
    shutil.copy('./config/Dockerfile', './image')
    os.mkdir('./image/config')
    copy_tree('./config/spark/config', './image/config')
    os.chdir('./image')
    os.system('pwd')
    os.system('docker build . -t {}'.format(create_image_name(frameworks)))


def image_exists(image_name):
    #TODO: find a way to check if the image exists
    return False


def deploy(config):
    #TODO: Run the image:
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Take in the configuration file")
    parser.add_argument('--config', help='The config file')

    args = parser.parse_args()

    if not args.config:
        print('You need to pass in the config file. Run with --help for more info')
        sys.exit(0)

    try:
        config_filename = args.config
        config_file = open(config_filename)
        config = json.load(config_file)
    except FileNotFoundError:
        print('Error opening the config file')
        sys.exit(0)

    processing = ['library', 'engine', 'storage']
    frameworks = get_frameworks(config, processing)
    
    create_image(frameworks)
#    if not image_exists(config):
#        create_image(config)

