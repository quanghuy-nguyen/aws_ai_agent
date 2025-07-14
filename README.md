# Manufacturing Inspection AI Agent

## Overview
This project implements an AI-powered inspection system for manufacturing processes. It uses AWS Lambda with Docker containers, FastAPI, and LangChain to process images, extract data using OCR, compare production counts against reference values, and generate detailed inspection reports.

## Features
- **Image Processing**: Upload and process images to extract production counts using OCR (via OCR.Space API).
- **Data Comparison**: Compare extracted counts against predefined reference values to identify discrepancies.
- **Report Generation**: Generate detailed inspection reports with timestamps and save them as text files.
- **AI Agent Interaction**: Interact with an AI agent powered by LangChain and OpenAI's GPT-4o for processing and analyzing data.
- **AWS Deployment**: Deployed as a serverless application using AWS CDK with a Docker-based Lambda function.
- **API Endpoints**: FastAPI endpoints for uploading images, chatting with the AI agent, and downloading reports.

## Project Structure
```text
Report_ai_agent/
│
├── agent-cdk-infra/
│
├── image/
│   ├── .gitignore
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── ai_agent.py
│       ├── app_api_handler.py
│       └── tools.py
```


## Prerequisites
- **Python 3.8+**
- **Node.js** (for AWS CDK)
- **Docker** (for building Lambda container images)
- **AWS CLI** (configured with appropriate credentials)
- **Required Python packages** (listed in `requirements.txt`):
  - `aws-cdk-lib`
  - `langchain`
  - `langchain-openai`
  - `langchain-community`
  - `langchain-core`
  - `fastapi`
  - `mangum`
  - `uvicorn`
  - `pydantic`
  - `requests`
  - `python-dotenv`
  - `python-multipart`

- **Environment Variables**:
  - `OPENAI_API_KEY`: API key for OpenAI.
  - `OCR_SPACE_API_KEY`: API key for OCR.Space.
  - `IS_USING_IMAGE_RUNTIME`: Set to any value when running in a containerized environment (e.g., Lambda).

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/quanghuy-nguyen/aws_ai_agent
   cd aws_ai_agent
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install aws-cdk-lib constructs
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory:
   ```plaintext
   OPENAI_API_KEY=your-openai-api-key
   OCR_SPACE_API_KEY=your-ocr-space-api-key
   ```

4. **Build Docker Image**:
   Ensure the Docker daemon is running, and build the image for the Lambda function:
   ```bash
   docker build --platform linux/amd64 -t ai_agent_app .
   ```

5. **Deploy with AWS CDK**:
   ```bash
   cdk deploy
   ```
   This deploys the Lambda function and outputs the function URL.

6. **Run Locally (Optional)**:
   To test the FastAPI application locally:
   ```bash
   python app_api_handler.py
   ```
   The server will run at `http://localhost:8000`.

## Usage
### API Endpoints
- **GET /**: Returns a welcome message.
- **POST /upload_images**: Upload images for processing.
  - Request: Multipart form-data with image files (`.jpg` or `.png`).
  - Response: JSON with uploaded file names.
- **POST /chat**: Interact with the AI agent.
  - Request: JSON body with `message` field.
  - Response: JSON with the agent's response.
- **GET /download_report**: Download the latest inspection report.
  - Response: Text file with the latest report.

### Example Workflow
1. Upload images to `/upload_images`.
2. Use the `/chat` endpoint to:
   - List images with `list_images_in_folder`.
   - Process images with `process_multiple_images`.
   - Compare counts with `compare_count_values_to_reference`.
   - Generate a report with `generate_full_report_from_processed_results`.
3. Download the report from `/download_report`.

### Example Chat Commands
- List images: "List all images in the folder."
- Process images: "Process images: images/1.jpg