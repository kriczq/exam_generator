from flask import json, Response


def build_response(response_entity, status_code):
    if response_entity is not None:
        return Response(mimetype="application/json",
                        response=json.dumps(response_entity, default=__serialize),
                        status=status_code)
    else:
        return Response(status=status_code)


def __serialize(obj):
    return obj.serialize
