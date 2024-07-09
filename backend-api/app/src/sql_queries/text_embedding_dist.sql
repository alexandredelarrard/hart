SET LOCAL hnsw.ef_search = {limite};
SELECT "{id_item_lower}", ("embedding" <=> %s::vector) AS distance
FROM "{table}"
ORDER BY distance
LIMIT {limite};
