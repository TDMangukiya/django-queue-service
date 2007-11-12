from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils.encoding import smart_str, force_unicode
from django.utils import simplejson
from django.core import serializers
from django.conf import settings

_DEFAULT_FORMAT = hasattr(settings, 'DQS_REST_DEFAULT_OUTPUT_FORMAT') and settings.DQS_REST_DEFAULT_OUTPUT_FORMAT or 'json'

def check_allowed_methods(methods=['GET'], formats=['text', 'json', 'xml']):
    from django.http import HttpResponseForbidden
    '''
    Convenient decorator that verifies that a view is being called with 
    an allowed set of request methods and no others. Also, checks that the format 
    parameter is in the accepted list.
    
    Returns HttpResponseForbidden if view is called with a disallowed method or format
    '''
    def _decorator(view_func):
        def _wrapper(request, *args, **kwargs):
            format = request.REQUEST.get('format', _DEFAULT_FORMAT)
            if request.method in methods and format in formats:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        _wrapper.__doc__ = view_func.__doc__
        _wrapper.__dict__ = view_func.__dict__
        return _wrapper
    return _decorator


class Status(object):
    "DRY code to handle json and text format responses uniformly"

    def __init__(self, in_dict=None):
        self.format = in_dict and in_dict.get('format', _DEFAULT_FORMAT).lower() or _DEFAULT_FORMAT
        self.success = True
        self.error_message = None
        self.response_override = None
        self.result_object = None

    def _set_result(self, result_object):
        self.success = True
        self.result_object = result_object

    def _get_result(self):
        return self.result_object

    result = property(_get_result, _set_result)

    def _set_error(self, error_message):
        self.success = False
        self.error_message = error_message

    def _get_error(self):
        return self.error_message

    error = property(_get_error, _set_error)

    def __call__(self):
        return self._get_response()

    def _get_response(self):
        if self.response_override:
            return self.response_override
        response_method = '_%s_%s_response' % (self.format, self.success and 'success' or 'error')
        return getattr(self, response_method)()

    def _set_response(self, response):
        self.response_override = response

    response = property(_get_response, _set_response)

    # JSON handler
    def _json_error_response(self):
        err = {'error':self.error}
        return HttpResponse(simplejson.dumps(err),
                    mimetype='application/json; charset=%s' % settings.DEFAULT_CHARSET)

    def _json_success_response(self):
        response = HttpResponse(mimetype='application/json; charset=%s' % settings.DEFAULT_CHARSET)
        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(self.result, ensure_ascii=False, stream=response)
        return response

    # Plain text handler
    def _text_error_response(self):
         return HttpResponse(smart_str(self.error, settings.DEFAULT_CHARSET),
            mimetype='text/plain; charset=%s' % settings.DEFAULT_CHARSET)

    def _text_success_response(self):
        text = ''
        for item in self.result:
            text = text + '\n' + force_unicode(item)
        return HttpResponse(smart_str(text, settings.DEFAULT_CHARSET),
            mimetype='text/plain; charset=%s' % settings.DEFAULT_CHARSET)

    # XML handler
    def _xml_error_response(self):
        raise Exception("Not implemented")

    def _xml_success_response(self):
        response = HttpResponse(mimetype='text/xml; charset=%s' % settings.DEFAULT_CHARSET)
        if hasattr(self.result, '__iter__'):
            xml_serializer = serializers.get_serializer("xml")()
            xml_serializer.serialize(self.result, ensure_ascii=False, stream=response)
        return response