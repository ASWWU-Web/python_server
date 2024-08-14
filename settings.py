import os
import tomllib
import toml

# TODO: unflatten the config file
config = {
    'port': 0,
    'base_url': '',
    'log_name': '',
    'current_year': 0,
    'databases': '',
    'media_path': '',
    'developer_id': 0,
    'resumes': '',
    'temporary_files': '',
    'testing_databases': '',
}

def loadConfig(location = "./config.toml"):
    if os.path.exists(location):
        with open(location, "rb") as tmpCfg:
            tomlConfig = tomllib.load(tmpCfg)
            config['port'] =            tomlConfig['server']['port']
            config['base_url'] =        tomlConfig['server']['base_url']
            config['log_name'] =        tomlConfig['logging']['log_name']
            config['current_year'] =    tomlConfig['mask']['current_year']
            config['databases'] =       tomlConfig['database']['databases']
            config['media_path'] =      tomlConfig['media']['media_path']
            config['developer_id'] =    tomlConfig['development']['developer_id']
            config['resumes'] =         tomlConfig['forms']['resumes']
            config['temporary_files'] = tomlConfig['server']['temporary_files']
            config['testing_databases'] = tomlConfig['database']['testing_databases']
    else:
        print("No config file found, creating one...")
        makeConfig()
    


def buildMediaPath(subPath):
    return os.path.join(config['media_path'], subPath)

# currently hardcoded, but will be replaced with a config file
def setupTestingConfig():
    config['port'] = 8888
    config['base_url'] = 'http://localhost'
    config['log_name'] = 'aswwu'
    config['current_year'] = '2324'
    config['databases'] = './tmp/databases'
    config['media_path'] = './tmp/media'
    config['developer_id'] = 0
    config['resumes'] = './tmp/resume'
    config['temporary_files'] = './tmp'
    config['testing_databases'] = './testing_databases'

def setupConfig():
    config['port'] = 8888
    config['base_url'] = 'http://localhost'
    config['log_name'] = 'aswwu'
    config['current_year'] = '2324'
    config['databases'] = '../databases'
    config['media_path'] = '../media'
    config['developer_id'] = 2090791
    config['resumes'] = '../databases/resume'
    config['temporary_files'] = './tmp'
    config['testing_databases'] = './testing_databases'

    # write the config file
    with open('config.toml', 'rb+') as config_file:
        config_file.write(toml.dump(config))
        config_file.close()



def makeConfig():
    if os.environ['ENVIRONMENT'] == 'pytest':
        setupTestingConfig()
    else:
        setupConfig()
