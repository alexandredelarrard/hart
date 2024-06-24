CREATE DATABASE vectordb TEMPLATE template0 LC_COLLATE 'C' LC_CTYPE 'C';

\c vectordb;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Define your tables with constraints

CREATE TABLE text_embeddings (
  id SERIAL PRIMARY KEY,
  embedding vector,
  id_item text UNIQUE,
  created_at timestamptz DEFAULT now(),
  CONSTRAINT text_embeddings_id_item_unique UNIQUE (id_item)
);

CREATE TABLE picture_embeddings (
  id SERIAL PRIMARY KEY,
  embedding vector,
  id_unique text UNIQUE,
  created_at timestamptz DEFAULT now(),
  CONSTRAINT picture_embeddings_id_unique UNIQUE (id_unique)
);
