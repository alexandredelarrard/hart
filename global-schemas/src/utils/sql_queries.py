# -*- coding: utf-8 -*-
from pathlib import Path
from re import DOTALL, sub
from types import SimpleNamespace
from typing import Any, Dict, Optional
from src.utils.timing import timing

import sqlparse

SQL_FILE_ENDING = "sql"


class SQLQueries:
    """Class that handles the parsing and cleaning of SQL files.

    Args:
        query_folder_path: the path to the folder where the SQL queries we want to parse are located.
    """

    def __init__(self, query_folder_path: str) -> None:
        self.SQL = SimpleNamespace()
        all_sql = sorted(Path(query_folder_path).glob(f"*.{SQL_FILE_ENDING}"))
        for query in all_sql:
            query_name = query.stem

            with open(f"{query}", "r") as f:
                parsed_sql = "\n".join(
                    filter(
                        None,
                        [
                            sub(r"\s*--.*$", "", line, DOTALL)
                            for line in f.read().split("\n")
                        ],
                    )
                )
                # extra cleaning
                parsed_sql = sqlparse.format(
                    parsed_sql, reindent=True, keyword_case="upper"
                )

                # store query in namespace
                setattr(self.SQL, query_name, parsed_sql)

    @staticmethod
    def format_query(query: str, query_params: Optional[Dict[str, Any]] = None) -> str:
        """Formats a supplied query with the supplied `query_params`

        Args:
            query: the query that is to be formatted. can be multiple sub-queries.
            query_params: Parameters to interpolate. Default to None.

        Returns:
            str: An interpolated instance of the supplied query
        """
        return query.format(**(query_params if query_params is not None else {}))
