SELECT main."{id_item}", main."{item_title_detailed}", main."{total_description}"
FROM "{table}" main
LEFT JOIN "{raw_table_gpt}" raw
ON main."{id_item}" = raw."{id_item_gpt}"
WHERE raw."{id_item_gpt}" IS NULL;
