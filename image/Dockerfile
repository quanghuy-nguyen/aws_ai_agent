FROM public.ecr.aws/lambda/python:3.12

ENV IS_USING_IMAGE_RUNTIME = True

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install --no-cache-dir -r requirements.txt --upgrade

# For local testing.
EXPOSE 8000

# Copy all files in ./src
COPY src/* ${LAMBDA_TASK_ROOT}
