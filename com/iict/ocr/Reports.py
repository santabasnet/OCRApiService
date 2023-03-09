# Error, Success reporting module part.
import imghdr
import json


# Format No file error message.
def noFileError():
    errMessage = {
        'id': 1,
        'status': 'fail',
        'message': 'No input file.'
    }
    return json.dumps(errMessage, indent=4)


# Format of the given input file is not processable.
def invalidFileError():
    errMessage = {
        'id': 2,
        'status': 'fail',
        'message': 'Format of the given input file is not processable.'
    }
    return json.dumps(errMessage, indent=4)


