# Multi-Tenant Farsi Chatbot

این پروژه یک چت‌بات پشتیبانی چند مستاجره (Multi-Tenant) برای فروشگاه‌های آنلاین است که با استفاده از Rasa و Flask در محیط Docker پیاده‌سازی شده است. این چت‌بات از زبان فارسی پشتیبانی می‌کند و برای استفاده روی VPS طراحی شده است.

## ویژگی‌ها

- پشتیبانی از چندین فروشگاه (چند مستاجره) با شناسه مخصوص هر فروشگاه
- پردازش زبان طبیعی فارسی با استفاده از Rasa
- API برای مدیریت پیام‌ها با استفاده از Flask
- احراز هویت با JWT و API Key
- ذخیره‌سازی اطلاعات در دیتابیس SQLite
- اجرا در محیط Docker

## ساختار پروژه

```
/opt/chatbot/
│── rasa/               # تنظیمات و مدل‌های Rasa
│── flask/              # API برای مدیریت پیام‌ها
│── data/               # داده‌های آموزشی چت‌بات
│── models/             # مدل‌های ذخیره‌شده Rasa
│── logs/               # لاگ‌های اجرا
│── docker-compose.yml  # تنظیمات Docker برای اجرای پروژه
│── .gitignore          # فایل‌های نادیده گرفته‌شده در Git
```

## پیش‌نیازها

- Docker
- Docker Compose
- Git

## نصب و راه‌اندازی

### 1. کلون کردن مخزن

```bash
git clone [آدرس مخزن]
cd /opt/chatbot
```

### 2. ایجاد داده‌های اولیه

```bash
cd data
python generate_tenants.py
cd ..
```

### 3. ساخت و اجرای کانتینرها

```bash
docker-compose build
docker-compose up -d
```

### 4. آموزش مدل Rasa

```bash
docker-compose exec rasa rasa train --domain domain.yml --data data --out models
```

### 5. بررسی وضعیت سرویس‌ها

```bash
docker-compose ps
```

## نحوه استفاده از API

### احراز هویت و دریافت توکن JWT

```bash
curl -X POST http://localhost:8000/auth \
  -H "X-API-Key: [API Key فروشگاه]" \
  -H "X-Tenant-ID: [شناسه فروشگاه]"
```

### ارسال پیام به چت‌بات

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Authorization: Bearer [توکن JWT]" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "سلام چطور می‌توانم محصول را برگشت بدهم؟"
  }'
```

### دریافت لیست مکالمات

```bash
curl -X GET http://localhost:8000/conversations \
  -H "Authorization: Bearer [توکن JWT]"
```

### دریافت پیام‌های یک مکالمه

```bash
curl -X GET http://localhost:8000/conversations/[شناسه مکالمه]/messages \
  -H "Authorization: Bearer [توکن JWT]"
```

## امنیت و توصیه‌ها

1. در محیط تولید، کلید رمزنگاری امن برای JWT تنظیم کنید.
2. از HTTPS برای ارتباطات استفاده کنید.
3. IP‌های مجاز را در فایروال محدود کنید.

## توسعه و مشارکت

1. ابتدا یک شاخه (branch) جدید ایجاد کنید
2. تغییرات خود را اعمال کنید
3. تست‌ها را اجرا کنید
4. درخواست ادغام (Pull Request) ارسال کنید