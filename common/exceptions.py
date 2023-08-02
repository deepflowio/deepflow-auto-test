class AutomationException(Exception):
    message = None
    status = None

    def __init__(self, message, status='FAIL'):
        Exception.__init__(self)
        self.message = message
        self.status = status

    def __str__(self):
        return 'Error (%s): %s' % (self.status, self.message)


class BadRequestException(AutomationException):
    pass


class InternalServerErrorException(AutomationException):
    pass


class NotFoundException(AutomationException):
    pass


class VerityException(AutomationException):
    pass


class ExecRunnerException(AutomationException):
    pass


class EnvDeployException(AutomationException):
    pass
