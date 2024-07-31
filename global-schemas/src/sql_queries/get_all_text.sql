SELECT
    text_table."{id_item}",
    text_table."{detail_title}",
    text_table."{total_description}",
    CONCAT(text_table."{detail_title}", '\n', text_table."{total_description}") AS target
FROM
    "{table_name}" as text_table
LEFT JOIN
    "{text_embedding_table}" as embedding
ON
    text_table."{id_item}" = embedding."{id_item}"
WHERE
    embedding."{id_item}" IS NULL
    AND LENGTH(CONCAT(text_table."{detail_title}", '\n', text_table."{total_description}")) > {string_limit}
LIMIT
    {limite}
