FROM python:3.10

RUN mkdir /app 

COPY /unifai /app/unifai
# COPY pyproject.toml /app 
# COPY README.md /app

WORKDIR /app 

RUN pip3 install -r requirements.txt
RUN python3 unifai/TTTT.py
CMD ["python3", "unifai/server.py"]

# ENV PYTHONPATH=${PYTHONPATH}:${PWD}

# RUN pip3 install poetry 
# RUN poetry config virtualenvs.create false
# RUN poetry install --only main

# RUN poetry run preload_models

# CMD ["poetry", "run", "server"]
