SET LOCAL hnsw.ef_search = {limite};
SELECT DISTINCT "{id_item_lower}", ("embedding" <=> {embedding}::vector) AS distance
FROM "{table}"
ORDER BY distance
LIMIT {limite};
