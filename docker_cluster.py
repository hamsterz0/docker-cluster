import json
import hashlib
import os
import sys

def read_config_file(config):
    try:
        config = json.load(open(config))
    except FileNotFoundError:
        print('Error opening the config file')
        sys.exit(0)
    return config

def read_file(path):
    contents = []
    with open(path, 'r') as f:
        for line in f:
            contents.append(line)
    return contents

class DockerCluster:
    """
        Handles the initialization and creation of Docker containers. 
    """
    def __init__(self, config):
        self.info = read_config_file(config)
        self.image = Image(self.info['image'])
    
    def deploy(self):
        """
            Deploy the network.
        """
        # TODO: @Ken, deloy code here. 
        pass

    def run(self):
        """
            Initial run method.
        """
        if not self.image.exists():
            self.image.create()
        else:
            print('Image exists -- Test')
        self.deploy()


class Image:
    """
        Creates or returns the image
    """
    def __init__(self, info):
        self.info = info
        self.framework = Framework(self.info['framework'])

    def create(self):
        """
            Method to create the image. 
        """
        # Checking for the framework support. 
        if not self.framework.support():
            print('''Unfortunately, we don\'t support one or more of the frameworks 
                     you have listed in your config file. Please read the docs for
                     more information. Thank you.''')
            sys.exit(0)     # Better to throw an exception instead but meeeh.
        # Working on creating an image. 
        if os.path.isdir(self.image_name):
            os.system('rm -rf '+self.image_name)
        os.mkdir(self.image_name)                                                  # Creating a image_dir
        docker_file_contents = self.framework.docker_contents(self.image_name)     # Getting the contents for the docker file
        docker_file_path = self.image_name + '/Dockerfile'                         # Getting the path to the Docker file
        os.system('touch ' + docker_file_path)                                     # Creating a new Docker file at that path loc. 
        with open(docker_file_path, 'w') as df:
            for line in docker_file_contents:
                df.write(line)
        os.system('docker build ./' + self.image_name + ' -t ' + self.image_name)   # Build the image.

    def exists(self):
        """
            Method to check if the image exists. 

            Returns the image name.
        """
        image_list = os.popen('docker image ls').read()
        print(self.image_name)
        return self.image_name in [names.split(' ')[0] for names in image_list.split('\n')]

    @property
    def image_name(self):
        """
            Returns the image name
        """
        unique_str = ''.join(["'%s':'%s';"%(key, val) for (key, val) in sorted(self.info.items())]).encode('utf-8')
        return hashlib.sha1(unique_str).hexdigest()


class Framework:
    """
        This is the umbrella class for the parent
    """
    def __init__(self, info):
        self.name = info['name']
        self.base = 'config/'
        self.computation = ComputationEngine(info['computation'], self.base)
        self.resource_man = ResourceManager(info['resource_manager'], self.base)        # Can't use this right now. 
    
    def docker_contents(self, image_name):
        """
            Upper level function to return the contents that need
            to be in the Dockerfile

            Returns
            --------
                docker_contents     -- list of all the commands.
        """
        docker_contents = []
        # adding the base config (SSH and stuff). 
        docker_contents.extend(read_file(self.base + 'base_config'))
        # adding the hadoop config
        docker_contents.extend(read_file(self.base + self.name + '/' + self.name + '_config'))
        # adding the computation engines config
        docker_contents.extend(self.computation.docker_contents(image_name))
        return docker_contents

    def support(self):
        """
            Checks if we support the computation engine or not. 

            Returns
            --------
                Boolean     -- If we can support or not. 
        """
        if self.computation.support():          # self.computation.support() and self.resource_man.support()
            return True
        return False


class Engine:
    """
        Parent class for the Computation Engine and the
        Resource Manager Engine
    """
    def __init__(self, info, base):
        self.base = base
        self.name = self.name = info['name']

    def support(self):
        """
            Checks if we support the computation engine or not. 

            Returns
            --------
                Boolean     -- If we can support or not. 
        """
        support_list = os.popen('ls ' + self.base).read()
        return self.name in [names.split(' ')[0] for names in support_list.split('\n')]

    def docker_contents(self):
        """
            Contents for the computation engine that need to be in the Dockerfile

            Returns
            --------
                docker_contents     -- list of all the commands.
        """
        docker_contents = []
        docker_contents.extend(read_file(self.config_path + '/' + self.name + '_config'))
        return docker_contents
    
    @property
    def config_path(self):
        return self.base + self.name



class ComputationEngine(Engine):
    """
        This takes care of the updates and XML's of 
        the computation engine used (Spark, MapReduce etc. )
    """
    def __init__(self, info, base='config/'):
        super().__init__(info, base)
        # TODO: Add more here @TANMAY
    
    def update_config_files(self):
        # TODO: @Tanmay -> this is where you can update the config files
        pass

    def docker_contents(self, image_name):
        docker_contents = super().docker_contents()
        config_folder = self.base + self.name + '/config/.'
        # update the XML files
        self.update_config_files()
        os.system('cp -r ' + config_folder + ' ' + image_name + '/config')
        return docker_contents


class ResourceManager(Engine):
    """
        This takes care of the updates and XML's of 
        the resource manager used
    """
    def __init__(self, info, base='config/'):
        super().__init__(info, base)
        # TODO: Add more here @TANMAY


if __name__ == '__main__':
    dockerCluster = DockerCluster('sample_config.json')
    dockerCluster.run()
