SELECT DISTINCT "{id_item}", "{id_picture}", "{date}", "{localisation}", "{seller}", "{url_full_detail}", "{country}", "{auction_title}", "{total_description}", "{eur_min_estimate}", "{eur_max_estimate}", "{eur_item_result}", "{min_estimate}", "{max_estimate}", "{item_result}", "{is_item_result}", "{currency}"  
FROM "{table_name}"
WHERE "{id_picture}" IS NOT NULL
