from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from sqlalchemy.exc import SQLAlchemyError

os.chdir(r"C:\Users\alarr\Documents\repos\hart\backend-art-analytics")
from src.context import get_config_context

# Define the SQL commands to drop and recreate indexes
INDEX_COMMANDS = [
    """
    DROP INDEX IF EXISTS picture_embeddings_embedding_idx;
    CREATE INDEX picture_embeddings_embedding_idx
    ON picture_embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 128, ef_search = 100);
    """,
    """
    DROP INDEX IF EXISTS text_embeddings_english_embedding_idx;
    CREATE INDEX text_embeddings_english_embedding_idx
    ON text_embeddings_english USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 128, ef_search = 100);
    """,
    """
    DROP INDEX IF EXISTS text_embeddings_french_embedding_idx;
    CREATE INDEX text_embeddings_french_embedding_idx
    ON text_embeddings_french USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 128, ef_search = 100);
    """,
]


def recreate_indexes(engine):
    with engine.connect() as connection:

        # Set maintenance_work_mem for the session
        connection.execute(text("SET max_parallel_workers = 8;"))
        connection.execute(text("SET max_parallel_workers_per_gather = 4;"))
        connection.execute(text("SET maintenance_work_mem = '2GB';"))

        for command in INDEX_COMMANDS:
            try:
                connection.execute(text(command))
                print("Index recreated successfully.")
            except SQLAlchemyError as e:
                print(f"An error occurred: {e}")


def reset_conn(context):
    # Create a configured "Session" class
    Session = sessionmaker(bind=context.db_con)

    # Create a session
    session = Session()
    session.rollback()
    session.close()


if __name__ == "__main__":
    config, context = get_config_context("./configs", use_cache=False, save=False)
    recreate_indexes(context.db_con)
