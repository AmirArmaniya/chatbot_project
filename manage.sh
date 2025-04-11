#!/bin/bash

# فایل مدیریت چت‌بات
# استفاده: ./manage.sh [start|stop|restart|build|logs|train]

set -e

cd "$(dirname "$0")"

case "$1" in
  start)
    echo "شروع اجرای سرویس‌ها..."
    docker-compose up -d
    echo "سرویس‌ها با موفقیت شروع شدند."
    ;;
    
  stop)
    echo "توقف سرویس‌ها..."
    docker-compose down
    echo "سرویس‌ها متوقف شدند."
    ;;
    
  restart)
    echo "راه‌اندازی مجدد سرویس‌ها..."
    docker-compose down
    docker-compose up -d
    echo "سرویس‌ها مجدداً راه‌اندازی شدند."
    ;;
    
  build)
    echo "ساخت تصاویر..."
    docker-compose build
    echo "تصاویر با موفقیت ساخته شدند."
    ;;
    
  logs)
    echo "نمایش لاگ‌ها..."
    docker-compose logs -f
    ;;
    
  train)
    echo "آموزش مدل Rasa..."
    docker-compose run --rm rasa train
    echo "آموزش مدل با موفقیت انجام شد."
    ;;
    
  *)
    echo "استفاده: $0 [start|stop|restart|build|logs|train]"
    exit 1
    ;;
esac

exit 0