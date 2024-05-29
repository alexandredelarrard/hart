# Broker settings.
broker_url = 'redis://redis:6379/0'

# Backend settings.
result_backend = 'redis://redis:6379/0'

# Task serialization and deserialization settings.
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']  # Ignore other content

# Timezone and UTC settings.
timezone = 'UTC'
enable_utc = True

# Other Celery settings.
worker_prefetch_multiplier = 1
task_acks_late = True