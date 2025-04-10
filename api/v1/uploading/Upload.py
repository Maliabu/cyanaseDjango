# All Things related to modules
from api.helper import helper
from ..users.Users import Users

_user = Users()


# master module class
class Upload:
    def __init__(self):
        self.help = helper.Helper()

    def upload(self, output, file):
        destination = open(output, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()

    ##################
