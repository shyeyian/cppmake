from cppmakelib.basic.config          import config
from cppmakelib.error.config          import ConfigError
from cppmakelib.execution.operation   import when_all
from cppmakelib.execution.scheduler   import scheduler
from cppmakelib.file.file_import      import import_file
from cppmakelib.file.file_system      import exist_file, exist_dir, create_dir
from cppmakelib.logger.package_status import package_status_logger
from cppmakelib.utility.decorator     import once, syncable, trace, unique

class Package:
    @syncable
    @unique
    @trace
    async def __ainit__(self, name):
        self.name            = name
        self.dir             = Package._search(name)
        self.git_dir         = f'{self.dir}/git'
        self.module_dir      = f'{self.dir}/module'
        self.cppmake_file    = f'{self.dir}/cppmake.py'
        self.build_dir       = f'binary/package/{self.name}/build'
        self.install_dir     = f'binary/package/{self.name}/install'
        self.include_dir     = f'binary/package/{self.name}/install/include'
        self.import_dir      = f'binary/package/{self.name}/install/import'
        self.lib_dir         = f'binary/package/{self.name}/install/lib'
        self.depend_packages = [] # defined in cppmake.py
        self.compile_flags   = [] # defined in cppmake.py
        self.define_macros   = {} # defined in cppmake.py
        self.link_flags      = [] # defined in cppmake.py
        self.cppmake         = import_file(self.cppmake_file, globals={'self': self}) if exist_file(self.cppmake_file) else None

    @syncable
    @once
    @trace
    async def async_build(self):
        if not await self.async_is_built():
            await when_all([package.async_build() for package in self.depend_packages])
            async with scheduler.schedule(scheduler.max):
                print(f'build package: {self.name}')
                create_dir(self.build_dir)
                create_dir(self.install_dir)
                self.cppmake.build() if hasattr(self.cppmake, 'build') else None
            await package_status_logger.async_log(package=self)

    @syncable
    @once
    async def async_is_built(self):
        return all(await when_all([package.async_is_built() for package in self.depend_packages])) and \
               await package_status_logger.async_query(package=self)
    
    def _search(name):
        return '.' if name == '.' else \
               f'package/{name}' if 

        if name == '.':
            return '.'
        else:
            dir = f'package/{name}'
            if exist_dir(dir):
                return dir
            else:
                raise ConfigError(f'package {name} is not found')
