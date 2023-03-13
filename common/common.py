from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.encoding import force_str


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_str(detail)}
        else: self.detail = {'detail': force_str(self.default_detail)}


def getFirstError(errors):
    msg = ""
    for error in errors:
        if isinstance(errors[error], dict):
            for error2 in errors[error]:
                msg = errors[error][error2][0]
        else:
            if isinstance(errors[error][0], dict):
                for error2 in errors[error][0]:
                    msg =  errors[error][0][error2][0]
            else:
                if errors[error][0].startswith('This'):
                    msg = error + errors[error][0][4:]
                else:
                    msg =  errors[error][0]
    return {"message" : msg}