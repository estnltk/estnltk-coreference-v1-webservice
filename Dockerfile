FROM python:3.9

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        gcc \
        g++ \
        libffi-dev \
        musl-dev

ENV PYTHONIOENCODING=utf-8
ENV MKL_NUM_THREADS=16
WORKDIR /app

RUN adduser --disabled-password --gecos "app" app && \
    chown -R app:app /app
USER app

ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app requirements.txt .
RUN pip install --user -r requirements.txt && \
    rm requirements.txt && python -c "import stanza; stanza.download('et', model_dir='stanza_resources')"

RUN wget https://s3.hpc.ut.ee/estnltk/estnltk_resources/coreference_model_2021-01-04.zip && \
    unzip coreference_model_2021-01-04.zip && \
    rm coreference_model_2021-01-04.zip

COPY --chown=app:app . .

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--proxy-headers"]