-- Connect to the vectordb database
\c vectordb;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Define your tables with constraints
CREATE TABLE IF NOT EXISTS text_embeddings (
  ID_ITEM text PRIMARY KEY UNIQUE,
  CREATED_AT timestamptz DEFAULT now(),
  EMBEDDING VECTOR(1024),
  CONSTRAINT text_embeddings_id_item_unique UNIQUE (ID_ITEM)
);

CREATE TABLE IF NOT EXISTS picture_embeddings (
  ID_UNIQUE text PRIMARY KEY UNIQUE UNIQUE,
  ID_PICTURE Varchar,
  pict_path Varchar,
  CREATED_AT timestamptz DEFAULT now(),
  EMBEDDING VECTOR(1024),
  CONSTRAINT picture_embeddings_id_unique UNIQUE (ID_UNIQUE)
);

-- Disable autovacuum
ALTER TABLE text_embeddings SET (autovacuum_enabled = false);
ALTER TABLE picture_embeddings SET (autovacuum_enabled = false);

-- Set maintenance work memory and parallel workers
-- SET maintenance_work_mem TO '1GB';
-- SET max_parallel_maintenance_workers TO 3;

-- Load data from CSV file
COPY picture_embeddings FROM '/tmp/picture_embeddings.csv' WITH (FORMAT csv, HEADER true);

-- Create indexes on embedding columns
CREATE INDEX ON picture_embeddings USING hnsw (EMBEDDING vector_cosine_ops) WITH (m = 16, ef_construction=64);
CREATE INDEX ON text_embeddings USING hnsw (EMBEDDING vector_cosine_ops) WITH (m = 16, ef_construction=64);

-- Re-enable autovacuum
ALTER TABLE text_embeddings SET (autovacuum_enabled = true);
ALTER TABLE picture_embeddings SET (autovacuum_enabled = true);