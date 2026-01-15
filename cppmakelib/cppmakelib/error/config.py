from cppmakelib.utility.color import red, bold

class ConfigError(Exception):
    def __init__(self, message):
        super().__init__(f'{red(bold('fatal error:'))} {message}')

    def add_prefix(self, prefix):
        return ConfigError(f'{prefix}\n{self}')
