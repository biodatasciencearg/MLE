FROM python:3.8

COPY ./API/requirements.txt ./api/api/requirements.txt 

RUN pip install --no-cache-dir --upgrade -r api/api/requirements.txt


COPY ./API /api/api

ENV PYTHONPATH=/api
WORKDIR /api

EXPOSE 8000

ENV  KUESKI_FEATURE_STORE_API_URL="http://localhost:8000"
ENV KUESKI_FEATURE_STORE_PATH="sqlite:///feature_store_online.db"
ENV KUESKI_MODEL_PATH="./api/model_risk.joblib"

#ENTRYPOINT ["uvicorn"]
#CMD ["api.main:app","--proxy-headers", "--host", "127.0.0.1", "--port", "8000"]
CMD ["python", "./api/main.py"]
