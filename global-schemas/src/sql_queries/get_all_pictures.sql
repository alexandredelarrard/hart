SELECT
    pict_table."{id_picture}",
    pict_table."{seller}",
    CONCAT_WS(
        '/',
        '{root}',
        pict_table."{seller}",
        'pictures',
        CONCAT(pict_table."{id_picture}", '.jpg')
    ) AS target
FROM
    "{table_name}" as pict_table
LEFT JOIN
    "{picture_embedding_table}" as embedding
ON
    pict_table."{id_picture}" = embedding."{id_picture}"
WHERE
    pict_table."{is_file}" = true
    AND embedding."{id_picture}" IS NULL
LIMIT
    {limite}
