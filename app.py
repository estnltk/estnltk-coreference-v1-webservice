import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from estnltk_core.common import load_text_class
from estnltk_core.converters import layer_to_dict, json_to_layers

from coreference_tagger import CoreferenceTagger
from settings import settings


logger = logging.getLogger(__name__)

app = FastAPI(redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

Text = load_text_class()
# coreference_dir must be an absolute path
tagger = CoreferenceTagger(
    output_layer='coreference_v1', 
    resources_dir=os.path.abspath(settings.coreference_dir),
    stanza_models_dir=settings.stanza_models_dir,
    add_chain_ids=False
)

class Request(BaseModel):
    text: str = Field(...)
    meta: dict = Field(...)
    layers: str = Field(...)
    output_layer: str = Field(None)
    parameters: dict = Field(None)


@app.post('/estnltk/tagger/coreference_v1')
def tagger_coreference_v1(body: Request):
    if len(str(body)) > settings.max_content_length:
        raise HTTPException(status_code=413, detail="Request body too large")
    try:
        logger.debug(body)
        text = Text(body.text)
        text.meta = body.meta
        layers = json_to_layers(text, json_str=body.layers)
        for layer in Text.topological_sort(layers):
            text.add_layer(layer)
        layer = tagger.make_layer(text, layers)
        if body.output_layer is not None:
            layer.name = body.output_layer
        return layer_to_dict(layer)
    
    except ValueError as e:
        # If tagger.make_layer throws a ValueError, report about a missing layer
        raise HTTPException(status_code=400, detail='Error at input processing: {}'.format(str(e)))
    except Exception:
        logger.exception('Internal error at input processing')
        raise HTTPException(status_code=500, detail='Internal error at input processing')

@app.get('/estnltk/tagger/coreference_v1/about')
def tagger_coreference_v1_about():
    return 'Tags pronominal coreference using EstNLTK CoreferenceTagger\'s webservice. '+\
           'Based on EstonianCoreferenceSystem v1.0.0.'


@app.get('/estnltk/tagger/coreference_v1/status')
def tagger_coreference_v1_status():
    return 'OK'

