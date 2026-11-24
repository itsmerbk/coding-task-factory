FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git bash && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN git clone https://github.com/pallets/click.git /app && git checkout 934813e4d421071a1b3db3973c02fe2721359a6e
RUN pip install --no-cache-dir -e . pytest
