from cppmake.file.file_import import import_file

module = import_file("cppmake.py", to_config=True)
module.build()