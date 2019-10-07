from xhtml2pdf import pisa
from flask import json, Response


def serialize(obj):
    return obj.serialize


def make_response(res, status_code):
    if (res is not None):
        return Response(mimetype="application/json",
                        response=json.dumps(res, default=serialize),
                        status=status_code)
    else:
        return Response(status=status_code)


def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            sourceHtml,                # the HTML to convert
            dest=resultFile)           # file handle to recieve result

    # close output file
    resultFile.close()                 # close output file

    # return True on success and False on errors
    return pisaStatus.err
