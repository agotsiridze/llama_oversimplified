FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
git \
curl \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /workplace

ENV PYTHONUNBUFFERED=1

COPY ./workplace/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD ["tail", "-f", "/dev/null"]
