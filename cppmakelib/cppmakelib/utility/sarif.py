from cppmakelib.basic.config   import config
from cppmakelib.utility.inline import raise_
import re

class ClangWarning:
    ...

class ClangError:
    def __init__(self, context):
        self.message = ...
        

class ClangNote:
    ...

class Diagnose:
    def parse(self, context):
        path = r'[\w\.\+-\*/\\]+'
        groups = re.match(..., context)
        self.level

class Sarif(dict):
    def __init__(self, context):
        self["version"] = "2.1.0"
        self["runs"] = [
            {
                "originalUriBaseIds": {
                    "PWD": {
                        "uri": ...
                    }
                },
                "results": []
            }
        ]
        try:
            while True:
                self.mount(SarifResult(context))
        except:
            pass

    def mount(self, sarif_result):
        self["runs"][0]["results"] += [sarif_result]

class SarifResult(dict):
    def __init__(self, context):        
        diagnose = Diagnose(context)
        if diagnose.level not in ["fatal error", "error", "warning"]:
            raise ParseError(context)
        self["level"] = diagnose.level
        self["message"] = {
            "text": diagnose.message
        }
        self["locations"] = [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": diagnose.path,
                    **({"uriBaseId": "PWD"} if is_absolute_path(diagnose.path) else {})
                    }
                }
            }
        ]
        self["relatedLocations"] = []
        try:
            while True:
                self.mount(SarifRelatedLocation(context))
        except:
            pass

    def mount(self, sarif_related_location):
        if sarif_related_location.category == SarifRelatedLocation.candicate_:
            self["locations"][x]
        if sarif_related_location.category == SarifRelatedLocation.while_:
            self.mount_cache += [sarif_related_location]
        elif sarif_related_location.category == SarifRelatedLocation.because:
            
        
class SarifRelatedLocation(dict, Diagnose):
    while_ = 0

    def __init__(self, line):
        diagnose = re.match(rf'^({Diagnose.path}):({Diagnose.line}):({Diagnose.column}): ({Diagnose.level}): ({Diagnose.message})$', context.current())


class SarifAst:
    
        

        
class ParseError(Exception):
    pass



class _SarifFile:
    def __init__(self):
        self.version = "2.0.0",
        self.runs = ...

path_regex    = r'[\w\./\\]'
line_regex    = r'\d+'
column_regex  = r'\d+'
level_regex   = r'fatal error|error|warning|note'
message_regex = r'.*'
regex         = rf'^({path_regex}):({line_regex}):({column_regex}): ({level_regex}): ({message_regex})$'

class _SarifResult:

    def __init__(self, context):
        path, line, column, level, message = re.search(regex, context.current_line()).groups() or


        matches = rf'^({path_regex}):({line_regex}):({column_regex}): ({level_regex}): ({message_regex})$'


        self.ruleId = _search(r'(fatal error):', context.current_line()) or \
                      _search(r'(error):',       context.current_line()) or \
                      _search(r'\[(-W[\w-]+)\]', context.current_line()) or raise_(_ParseError())
        self.level  = _search(r'(fatal error):', context.current_line()) or \
                      _search(r'(error):',       context.current_line()) or \
                      _search(r'(warning):',     context.current_line()) or \
                      _search(r'(note):',        context.current_line()) or raise_(_ParseError())
        self.message = {
            "text": _search(rf'{self.level}: (.*)$', context.current_line()) or raise_(_ParseError())
        }
        self.locations = [
            {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "...",
                     **{"uriBaseId": "PWD"} if _is_relative_path(_search(r'(\w+):\d+:\d+: {self.level}: .*$' context.current_line())
                    },
                    "region": {
                        "startLine": 0, ##
                        "startColumn": 0, ##
                        "endLine": 1, ##
                        "endColumn": 1 ##
                    },
                    "contextRegion": ...
                },
                "logicalLocations": [...],
                "id": ...,
                "relationships": [...],
            }
        ]
        self.relatedLocations = ...
        

def make_sarif(error):
    for line in error.splitlines():
        






    return {
        "version": "2.0.0",
        "runs": [
            {
                "tool": {...},
                "invocations": [...],
                "originalUriBaseIds": {
                    "PWD": ... #####
                },
                "artifacts": {},
                "results": results
            }
        ]
    }


