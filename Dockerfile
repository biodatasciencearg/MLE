FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./API/requirements.txt ./app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r app/requirements.txt

COPY ./API /app
WORKDIR /app

EXPOSE 8000
ENV  KUESKI_FEATURE_STORE_API_URL="http://localhost"
ENV KUESKI_FEATURE_STORE_PATH="sqlite:///feature_store_online.db"
ENV KUESKI_MODEL_PATH="./model_risk.joblib"
