SELECT DISTINCT "{id_item}", "{id_picture}", "{date}", "{localisation}", "{seller}", "{url_full_detail}", "{auction_title}", "{total_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{is_item_result}", "{currency}"  
FROM "{table_name}"
WHERE "{id_picture}" IS NOT NULL
