import argparse
import sys
import json
import pdb

def create_image_name(config):
    name = [framework for framework in config['processing']['framework']]
    name.append('base')
    # TODO: For now the name is just the framework name, later we can add more. 
    return ''.join(name)


def create_docker_file(config, dep): 
    def create_docker_file_helper(framework, dep, files):
        if 'dep' not in dep[framework]:
            files.append(dep[framework]['install'])
            return
        for depend in dep[framework]['dep']:
            create_docker_file_helper(depend, dep, files)
        files.append(dep[framework]['install'])

    base_dockerfile = dep['base']['install']
    files = [base_dockerfile]
    for framework in config['processing']['framework']:
        create_docker_file_helper(framework, dep, files) 

    with open('config/Dockerfile', 'w') as outfile:
        for fname in files:
            with open(fname) as f:
                for line in f:
                    outfile.write(line)


def create_image(config):
    dep = json.load(open('dependencies.json'))
    create_docker_file(config, dep)


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
    
    print(create_image_name(config))
    create_image(config)
#    if not image_exists(config):
#        create_image(config)

