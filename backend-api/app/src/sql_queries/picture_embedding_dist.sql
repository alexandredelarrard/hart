SET LOCAL hnsw.ef_search = {limite};
WITH dist_table AS (
     SELECT DISTINCT "{id_unique_lower}", "{id_picture_lower}", ("embedding" <=> {embedding}::vector) AS distance
    FROM "{table}"
    ORDER BY distance
    LIMIT {limite}
)
SELECT dist_table."{id_picture_lower}", dist_table.distance, LOWER(items_table."{id_item}") AS id_item
FROM dist_table
LEFT JOIN (
    SELECT DISTINCT "{id_unique}", "{id_item}"
    FROM "{table_all}"
) AS items_table
ON dist_table."{id_unique_lower}" = items_table."{id_unique}";
