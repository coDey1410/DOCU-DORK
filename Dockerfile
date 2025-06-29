FROM python:3.11
EXPOSE 8083
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY app.py ./

# Set AWS environment variables


ENTRYPOINT [ "streamlit", "run", "app.py", "--server.port=8083", "--server.address=0.0.0.0" ]
