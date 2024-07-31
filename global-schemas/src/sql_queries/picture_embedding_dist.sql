WITH embed AS (
    SELECT "{id_picture}",
           ("embedding" <=> %s::vector) AS distance
    FROM "{table}"
    ORDER BY distance
    LIMIT {limite}
)
SELECT embed."{id_picture}", embed.distance, pict_table."{list_id_item}"
FROM embed
LEFT JOIN (
    SELECT "{id_picture}", "{list_id_item}"
    FROM "{picture_table}"
) as pict_table
ON pict_table."{id_picture}" = embed."{id_picture}"
