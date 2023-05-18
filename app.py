import logging
from flask import request, abort
from flask_cors import CORS

from nauron import Nauron

import settings

logger = logging.getLogger("gunicorn.error")

# Define application
app = Nauron(__name__, timeout=settings.MESSAGE_TIMEOUT, mq_parameters=settings.MQ_PARAMS)
CORS(app)

coref = app.add_service(name=settings.SERVICE_NAME, remote=settings.DISTRIBUTED)

if not settings.DISTRIBUTED:
    from coreference_tagger_worker import CoreferenceV1TaggerWorker

    coref.add_worker(CoreferenceV1TaggerWorker())

#
# Endpoints for CoreferenceV1TaggerWorker
#

@app.post('/estnltk/tagger/coreference_v1')
def tagger_coreference_v1():
    if request.content_length > settings.MAX_CONTENT_LENGTH:
        abort(413)
    response = coref.process_request(content=request.json)
    return response

@app.get('/estnltk/tagger/coreference_v1/about')
def tagger_coreference_v1_about():
    return 'Tags pronominal coreference using EstNLTK CoreferenceTagger\'s webservice. '+\
           'Based on EstonianCoreferenceSystem v1.0.0.'


@app.get('/estnltk/tagger/coreference_v1/status')
def tagger_coreference_v1_status():
    return 'OK'


if __name__ == '__main__':
    app.run()
