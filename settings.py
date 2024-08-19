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
            'current_year': 0
        }
        self.forms = {
            'resumes': ''
        }
        
        self._deprecated = {}

        # let's immediately load the config on creation
        self.load()
    
    def load(self, location = "./config.toml"):
        if os.path.exists(location) and os.environ['ENVIRONMENT'] != 'pytest':
            with open(location, "rb") as tmpCfg:
                tomlConfig = tomllib.load(tmpCfg)
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
    
    def setupTestingConfig(self):
        self.server = {
            'port': 8888,
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
            'current_year': '2324'
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
            'current_year': '2324'
        }
        self.forms = {
            'resumes': '../databases/resume'
        }

    def save(self):
        with open('config.toml', 'w') as config_file:            
            toml.dump(self, config_file)
            config_file.close()

config = Config()


# config = {
#     'port': 0,
#     'base_url': '',
#     'log_name': '',
#     'current_year': 0,
#     'databases': '',
#     'media_path': '',
#     'developer_id': 0,
#     'resumes': '',
#     'temporary_files': '',
#     'testing_databases': '',
# }

# def loadConfig(location = "./config.toml"):
#     if os.path.exists(location):
#         with open(location, "rb") as tmpCfg:
#             tomlConfig = tomllib.load(tmpCfg)
#             config['port'] =            tomlConfig['server']['port']
#             config['base_url'] =        tomlConfig['server']['base_url']
#             config['log_name'] =        tomlConfig['logging']['log_name']
#             config['current_year'] =    tomlConfig['mask']['current_year']
#             config['databases'] =       tomlConfig['database']['databases']
#             config['media_path'] =      tomlConfig['media']['media_path']
#             config['developer_id'] =    tomlConfig['development']['developer_id']
#             config['resumes'] =         tomlConfig['forms']['resumes']
#             config['temporary_files'] = tomlConfig['server']['temporary_files']
#             config['testing_databases'] = tomlConfig['database']['testing_databases']
#     else:
#         print("No config file found, creating one...")
#         makeConfig()
    


def buildMediaPath(subPath):
    return os.path.join(config.media.get('media_path'), subPath)

# # currently hardcoded, but will be replaced with a config file
# def setupTestingConfig():
#     config['port'] = 8888
#     config['base_url'] = 'http://localhost'
#     config['log_name'] = 'aswwu'
#     config['current_year'] = '2324'
#     config['databases'] = './tmp/databases'
#     config['media_path'] = './tmp/media'
#     config['developer_id'] = 0
#     config['resumes'] = './tmp/resume'
#     config['temporary_files'] = './tmp'
#     config['testing_databases'] = './testing_databases'

# def setupConfig():
#     config['port'] = 8888
#     config['base_url'] = 'http://localhost'
#     config['log_name'] = 'aswwu'
#     config['current_year'] = '2324'
#     config['databases'] = '../databases'
#     config['media_path'] = '../media'
#     config['developer_id'] = 0
#     config['resumes'] = '../databases/resume'
#     config['temporary_files'] = './tmp'
#     config['testing_databases'] = './testing_databases'

#     # write the config file
#     with open('config.toml', 'w') as config_file:
#         tmpConfig = {
#             'server': {
#                 'port': config['port'],
#                 'base_url': config['base_url'],
#                 'temporary_files': config['temporary_files']
#             },
#             'database': {
#                 'databases': config['databases'],
#                 'testing_databases': config['testing_databases']
#             },
#             'logging': {
#                 'log_name': config['log_name'],
#                 'level': 'INFO'
#             },
#             'media': {
#                 'media_path': config['media_path']
#             },
#             'development': {
#                 'developer_id': config['developer_id']
#             },
#             'mask': {
#                 'current_year': config['current_year']
#             },
#             'forms': {
#                 'resumes': config['resumes']
#             }
#         }
#         toml.dump(tmpConfig, config_file)
#         config_file.close()



# def makeConfig():
#     if os.environ['ENVIRONMENT'] == 'pytest':
#         setupTestingConfig()
#     else:
#         setupConfig()
