# Web service for EstNLTK's coreference tagger v1

This is a web service for EstNLTK's [CoreferenceTagger v1](https://github.com/estnltk/estnltk/blob/f39588ff8865a0610d66bfbf72c51a919417e228/tutorials/nlp_pipeline/D_information_extraction/04_pronominal_coreference.ipynb).

The service is based on FastAPI and should be run as a Docker container using the included `Dockerfile`. The required models are automatically downloaded upon building the image.

The API uses the following endpoints:

- `POST /estnltk/tagger/coreference_v1` - the main endpoint for obtaining coreference annotations
- `GET /estnltk/tagger/coreference_v1/about` - returns information about the webservice
- `GET /estnltk/tagger/coreference_v1/status` - returns the status of the webservice

## Configuration

The service should be run as a Docker container using the included `Dockerfile`. The API is exposed on port `8000`. The following environment variables can be used to change webservice behavior:

- `COREFERENCE_DIR` - path to coreference model directory (`coreference/model_2021-01-04` by default).
- `STANZE_MODELS_DIR` - path to stanza's models directory (`stanza_resources` by default).
- `MAX_CONTENT_LENGHT` - maximum lenght of the POST request body size in characters.

The container uses uvicorn as the ASGI server. The entrypoint of the container is `["uvicorn", "app:app", "--host", "0.0.0.0", "--proxy-headers"]`. Any additional  [uvicorn parameters](https://uvicorn.dev/deployment/) can be passed to the container at runtime as CMD arguments.

## Getting required resources

When using the web service without Docker, you need to obtain the coreference model and stanza's parsing model for Estonian.  

* You can download _the coreference model_ from [`https://s3.hpc.ut.ee/estnltk/estnltk_resources/coreference_model_2021-01-04.zip`](https://s3.hpc.ut.ee/estnltk/estnltk_resources/coreference_model_2021-01-04.zip). Unpack the zipped content into root directory. After all necessary model files have been assembled, the local directory `coreference` should have the following structure:

        coreference/
        └── model_2021-01-04
            ├── estonian_configuration_files
            │   ├── estonian_cases.xml
            │   ├── estonian_catalog.xml
            │   ├── estonian_embeddings.xml
            │   ├── estonian_sentence_context.xml
            │   ├── estonian_syntactic_functions.xml
            │   └── estonian_tag_set.xml
            ├── estonian_resources
            │   ├── estonian_abstractness_lexicon
            │   │   └── abstractness_ET.txt
            │   ├── estonian_embeddings
            │   │   └── lemmas.cbow.s100.w2v.bin
            │   ├── estonian_global_mention_scores
            │   │   └── estonian_mentions_score.txt
            │   ├── estonian_mentions
            │   │   └── estonian_mentions.txt
            │   └── estonian_training_data_preprocessed
            │       ├── estonian-computed-features.txt
            │       └── estonian_training_corpus-sklearn.txt
            └── model_readme.md

* Install [stanza](https://stanfordnlp.github.io/stanza/#getting-started) and download _stanza's Estonian model_ via command: 
```
python -c "import stanza; stanza.download('et', model_dir='stanza_resources')"
```
After downloading, the local directory `stanza_resources` should have the following content:

        stanza_resources/
        ├── et
        │   ├── default.zip
        │   ├── depparse
        │   │   └── edt.pt
        │   ├── lemma
        │   │   └── edt.pt
        │   ├── pos
        │   │   └── edt.pt
        │   ├── pretrain
        │   │   └── edt.pt
        │   └── tokenize
        │       └── edt.pt
        └── resources.json



### Quick testing of the webservice

To quickly test if the webservice has been set up properly and appears to run OK, try the following `curl` query:

    curl http://127.0.0.1:8000/estnltk/tagger/coreference_v1 -H "Content-Type: application/json" -d '{"text": "Piilupart Donald, kes kunagi ei anna järele, läks uuele ringile. Ta kärkis ja paukus, kuni muusika vaikis ja pasadoobel seiskus. Mis sa tühja mässad, küsis rahvas.", "meta": {}, "layers": "{}", "output_layer": "coreference_v1"}'


Expected result:

    {"ambiguous":false,"attributes":[],"meta":{},"name":"coreference_v1","relations":[{"annotations":[{}],"named_spans":{"mention":[10,16],"pronoun":[18,21]}},{"annotations":[{}],"named_spans":{"mention":[10,16],"pronoun":[65,67]}},{"annotations":[{}],"named_spans":{"mention":[10,16],"pronoun":[133,135]}}],"secondary_attributes":[],"serialisation_module":"relations_v0","span_names":["pronoun","mention"]}