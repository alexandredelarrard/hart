SELECT "{id_item}", "{class_prediction}", "{picture_path}", "{text_vector}"
FROM "{table_name}" 
WHERE "{proba_var}" > {proba_threshold}