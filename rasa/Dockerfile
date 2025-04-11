FROM rasa/rasa:3.6.2-full

WORKDIR /app

COPY config.yml domain.yml credentials.yml endpoints.yml ./
COPY data ./data
COPY models ./models

USER root

# نصب وابستگی‌های سازگار با CPU قدیمی
RUN pip install --no-cache-dir \
    transformers==4.26.1 \
    torch==1.13.1 \
    sentencepiece \
    tensorflow-cpu==2.8.0 \
    "protobuf<3.21.0"

# غیرفعال کردن هشدارهای SSE
ENV TF_CPP_MIN_LOG_LEVEL=3

# حذف دانلود مدل Spacy (غیرضروری برای فارسی)
# RUN python -m spacy download en_core_web_md --no-cache-dir