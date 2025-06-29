# DOCU-DORK

A Streamlit application that allows users to upload PDF documents and ask questions about their content.

## Features

- Upload PDF documents
- Split documents into chunks
- Build vector store index
- Ask questions about the uploaded documents

## Requirements

- Python 3.11+
- Docker
- AWS credentials (for S3 storage)

## Running the Application

### Using Docker

```bash
docker pull utsav21w21q/docu-dark
docker run -p 8083:8083 utsav21w21q/docu-dark
```

Access the application at http://localhost:8083

### Local Development

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run app.py
```

## AWS Configuration

The application requires AWS credentials to store indices in S3. Set the following environment variables:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION
- S3_BUCKET_NAME

## License

MIT License

# DOCU-DORK
