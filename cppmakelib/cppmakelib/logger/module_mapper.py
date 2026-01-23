from cppmakelib.utility.filesystem import path

class ModuleMapperLogger:
    def mapper_file_of(self, import_dir: path) -> path: ...

module_mapper_logger: ModuleMapperLogger
