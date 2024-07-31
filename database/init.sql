-- Connect to the vectordb database
\c vectordb;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Define your tables with constraints
CREATE TABLE IF NOT EXISTS text_embeddings_english (
  id_item text PRIMARY KEY UNIQUE,
  date_creation timestamptz DEFAULT now(),
  embedding VECTOR(1024),
  CONSTRAINT text_embeddings_id_item_unique UNIQUE (id_item)
);

-- Define your tables with constraints
CREATE TABLE IF NOT EXISTS text_embeddings_french (
  id_item text PRIMARY KEY UNIQUE,
  date_creation timestamptz DEFAULT now(),
  embedding VECTOR(1024),
  CONSTRAINT text_embeddings_id_item_unique UNIQUE (id_item)
);

CREATE TABLE IF NOT EXISTS picture_embeddings (
  id_picture text PRIMARY KEY UNIQUE UNIQUE,
  date_creation timestamptz DEFAULT now(),
  embedding VECTOR(1024),
  CONSTRAINT picture_embeddings_id_unique UNIQUE (id_picture)
);

-- Disable autovacuum
ALTER TABLE text_embeddings_english SET (autovacuum_enabled = false);
ALTER TABLE text_embeddings_french SET (autovacuum_enabled = false);
ALTER TABLE picture_embeddings SET (autovacuum_enabled = false);

-- Set maintenance work memory and parallel workers
-- SET maintenance_work_mem TO '1GB';
-- SET max_parallel_maintenance_workers TO 3;

-- Load data from CSV file
-- COPY picture_embeddings FROM '/tmp/picture_embeddings.csv' WITH (FORMAT csv, HEADER true);

-- Create indexes on embedding columns
CREATE INDEX IF NOT EXISTS ON picture_embeddings USING hnsw (EMBEDDING vector_cosine_ops) WITH (m = 16, ef_construction=64, ef_search=96);
CREATE INDEX IF NOT EXISTS ON text_embeddings_english USING hnsw (EMBEDDING vector_cosine_ops) WITH (m = 16, ef_construction=64, ef_search=96);
CREATE INDEX IF NOT EXISTS ON text_embeddings_french USING hnsw (EMBEDDING vector_cosine_ops) WITH (m = 16, ef_construction=64, ef_search=96);

-- Re-enable autovacuum
ALTER TABLE text_embeddings_english SET (autovacuum_enabled = true);
ALTER TABLE text_embeddings_french SET (autovacuum_enabled = true);
ALTER TABLE picture_embeddings SET (autovacuum_enabled = true);
