from cppmakelib.utility.color import red, bold

class LogicError(Exception):
    def __str__(self):
        return f'{red(bold('fatal error:'))} {super().__str__()}'

