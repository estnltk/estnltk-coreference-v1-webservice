import logging
from typing import Dict
import os.path

from nauron import Response, Worker
from marshmallow import Schema, fields, ValidationError

from estnltk_core.common import load_text_class
from estnltk_core.converters import layer_to_dict
from estnltk_core.converters import json_to_layers

from coreference_tagger import CoreferenceTagger

import settings

logger = logging.getLogger(settings.SERVICE_NAME)

Text = load_text_class()

class CoreferenceV1TaggerRequestSchema(Schema):
    text = fields.Str(required=True)
    meta = fields.Raw(required=True)
    layers = fields.Str(required=True)
    output_layer = fields.Str(required=False)
    parameters = fields.Raw(required=False, allow_none=True)


class CoreferenceV1TaggerWorker(Worker):
    def __init__(self, coreference_dir: str = "coreference/model_2021-01-04",
                       stanza_models_dir: str = "stanza_resources"):
        self.schema = CoreferenceV1TaggerRequestSchema
        # coreference_dir must be an absolute path
        coreference_dir = os.path.abspath(coreference_dir)
        self.tagger = CoreferenceTagger( output_layer='coreference_v1', \
                                         resources_dir=coreference_dir, \
                                         stanza_models_dir=stanza_models_dir, \
                                         add_chain_ids=False)

    def process_request(self, content: Dict, _: str) -> Response:
        try:
            logger.debug(content)
            content = self.schema().load(content)
            text = Text(content["text"])
            text.meta = content["meta"]
            layers = json_to_layers(text, json_str=content['layers'])
            for layer in Text.topological_sort(layers):
                text.add_layer(layer)
            layer = self.tagger.make_layer(text, layers)
            if 'output_layer' in content.keys():
                layer.name = content['output_layer']
            # No need to do layer_to_json: Response obj will handle the conversion
            return Response(layer_to_dict(layer), mimetype="application/json")
        except ValidationError as error:
            return Response(content=error.messages, http_status_code=400)
        except ValueError as err:
            # If tagger.make_layer throws a ValueError, report about a missing layer
            return Response(content='Error at input processing: {}'.format(str(err)), http_status_code=400)
        except Exception as error:
            return Response(content='Internal error at input processing', http_status_code=400)


if __name__ == "__main__":
    worker = CoreferenceV1TaggerWorker(coreference_dir=settings.COREFERENCE_DIR,
                                       stanza_models_dir=settings.STANZA_MODELS_DIR)
    worker.start(connection_parameters=settings.MQ_PARAMS,
                 service_name=settings.SERVICE_NAME,
                 routing_key=settings.ROUTING_KEY)
