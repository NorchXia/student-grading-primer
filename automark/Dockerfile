FROM python:3.11-slim
WORKDIR /check
RUN pip install requests psycopg2-binary
COPY sanity_check.py private_tests.py ./
CMD ["python", "sanity_check.py"]
