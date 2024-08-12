import tomllib

config = {
    'port': 0,
    'base_url': '',
    'log_name': '',
    'current_year': 0,
    'databases': '',
    'media_path': '',
    'developer_id': 0,
    'resumes': '',
    'temporary_files': ''
}

def loadConfig():
    with open("./config.toml", "rb") as tmpCfg:
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
        
        print(config)

def buildMediaPath(subPath):
    return config['media_path'] + subPath
    