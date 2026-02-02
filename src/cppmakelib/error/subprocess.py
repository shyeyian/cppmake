class SubprocessError(Exception):
    def __init__(self, stderr, is_stderr_printed, code):
        super().__init__(stderr)
        self.is_stderr_printed = is_stderr_printed
        self.code              = code

    def __str__(self):
        return super().__str__() if not self.is_stderr_printed else ''
    