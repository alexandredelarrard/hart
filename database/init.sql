-- Connect to the vectordb database
\c vectordb;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Define your tables with constraints
CREATE TABLE IF NOT EXISTS text_embeddings (
  id BIGINT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
  ID_ITEM text UNIQUE,
  CREATED_AT timestamptz DEFAULT now(),
  EMBEDDING VECTOR(1024),
  CONSTRAINT text_embeddings_id_item_unique UNIQUE (ID_ITEM)
);

CREATE TABLE IF NOT EXISTS picture_embeddings (
  id BIGINT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
  ID_UNIQUE text UNIQUE,
  ID_PICTURE Varchar,
  pict_path Varchar,
  CREATED_AT timestamptz DEFAULT now(),
  EMBEDDING VECTOR(1024),
  CONSTRAINT picture_embeddings_id_unique UNIQUE (ID_UNIQUE)
);

-- Create indexes on embedding columns
CREATE INDEX ON picture_embeddings USING hnsw (EMBEDDING vector_cosine_ops);
CREATE INDEX ON text_embeddings USING hnsw (EMBEDDING vector_cosine_ops);