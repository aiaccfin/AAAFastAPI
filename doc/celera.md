[FastAPI API] 
      |
      | INSERT invoice
      V
[Postgres invoice table] ----+
                              |
                              | enqueue Celery task
                              V
[Redis] ------------------> [Celery Worker] 
                                     |
                                     | render invoice → embed → pgvector
                                     V
                           [Postgres vector table]


