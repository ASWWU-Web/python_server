import os
import tomllib
import toml

class Config:
    def __init__(self):
        self.server = {
            'port': 0,
            'base_url': '',
            'temporary_files': ''
        }
        self.database = {
            'databases': '',
            'testing_databases': ''
        }
        self.logging = {
            'log_name': '',
            'level': 'INFO'
        }
        self.media = {
            'media_path': ''
        }
        self.development = {
            'developer_id': 0
        }
        self.mask = {
            'current_year': ''
        }
        self.forms = {
            'resumes': ''
        }
        
        self._deprecated = {}

        # let's immediately load the config on creation
        self.load()
    
    def load(self, location = "./config.toml"):
        # if the file doesn't exist, docker will try to mount a directory
        # so we may encounter empty files to bypass it
        if os.path.exists(location) and os.environ['ENVIRONMENT'] != 'pytest' and os.stat(location).st_size > 0:
            with open(location, "rb") as tmpCfg:
                tomlConfig = tomllib.load(tmpCfg)
                # ok so we have a config file, let's load it
                self.server =            tomlConfig['server']
                self.database =          tomlConfig['database']
                self.logging =           tomlConfig['logging']
                self.media =             tomlConfig['media']
                self.development =       tomlConfig['development']
                self.mask =              tomlConfig['mask']
                self.forms =             tomlConfig['forms']
        else:
            print("No config file found, creating one...")
            self.make()

    def make(self):
        if os.environ['ENVIRONMENT'] == 'pytest':
            self.setupTestingConfig()
        else:
            self.setupConfig()
            self.save()
    def setupTestingConfig(self):
        self.server = {
            'port': 4688,
            'base_url': 'http://localhost',
            'temporary_files': './tmp'
        }
        self.database = {
            'databases': './tmp/databases',
            'testing_databases': './testing_databases'
        }
        self.logging = {
            'log_name': 'aswwu',
            'level': 'INFO'
        }
        self.media = {
            'media_path': './tmp/media'
        }
        self.development = {
            'developer_id': 0
        }
        self.mask = {
            'current_year': '2425'
        }
        self.forms = {
            'resumes': './tmp/resume'
        }
    
    def setupConfig(self):
        self.server = {
            'port': 8888,
            'base_url': 'http://localhost',
            'temporary_files': './tmp'
        }
        self.database = {
            'databases': '../databases',
            'testing_databases': './testing_databases'
        }
        self.logging = {
            'log_name': 'aswwu',
            'level': 'INFO'
        }
        self.media = {
            'media_path': '../media'
        }
        self.development = {
            'developer_id': 0
        }
        self.mask = {
            'current_year': '2425'
        }
        self.forms = {
            'resumes': '../databases/resume'
        }

    def save(self):
        with open('config.toml', 'w') as config_file:            
            toml.dump(self.asdict(), config_file)
            config_file.close()

    def asdict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None and not k.startswith('_')}

# global config object
config = Config()


def buildMediaPath(subPath):
    return os.path.join(config.media.get('media_path'), subPath)