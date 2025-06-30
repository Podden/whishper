FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

WORKDIR /app

COPY requirements.txt ./

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -qq update && \
    apt-get -qq install ffmpeg curl git python3 python3-pip && \
    rm -rf /var/lib/apt/lists/* &&\
    pip install --upgrade pip && \
    pip install -r requirements.txt &&\
    pip install python-multipart && \
    rm -rf /root/.cache/pip/

# Install system dependencies
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -qq update && \
    apt-get -qq install --no-install-recommends --allow-change-held-packages \
        python3 python3-pip python3-dev \
        ffmpeg curl git ca-certificates build-essential && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set SSL certificates for Python
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Create symlinks for python and pip
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Copy only requirements first and install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install python-multipart

# Now copy the rest of your code
COPY . .

# Cleanup
RUN apt-get purge -y --auto-remove build-essential curl git && \
    apt-get clean && \
    rm -rf /root/.cache/pip/ /var/lib/apt/lists/* /tmp/* /var/tmp/*

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
    CMD ["python3", "healthcheck.py"]

EXPOSE 8000
CMD ["python3", "main.py"]
