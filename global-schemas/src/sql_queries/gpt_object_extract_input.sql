SELECT main."{id_item}", main."{total_description}", main."{english_title}", main."{english_description}"
FROM "{gpt_translate_categorize}" main
LEFT JOIN "{raw_table_gpt}" raw
ON main."{id_item}" = raw."{id_item_gpt}"
    AND raw."{schema_prompt_col}" = '{schema_prompt_value}'
WHERE main."{category_object}" = '{object_value}'
  AND raw."{id_item_gpt}" IS NULL;
