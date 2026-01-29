ssh -i A:\native\datamond_gcp_key -L 8080:localhost:8080 leo@34.130.233.222

celery -A app.celery.celery_worker worker --loglevel=info --pool=solo