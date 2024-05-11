(SELECT DISTINCT "{id_item}", "{id_picture}", "{lot}", "{date}", "{localisation}", "{house}", "{seller}", "{url_full_detail}", "{auction_title}", "{item_title}", "{detailed_title}", "{item_description}", "{detailed_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{is_item_result}", "{currency}"  
FROM "{drouot_name}")
UNION ALL
(SELECT DISTINCT "{id_item}", "{id_picture}", "{lot}", "{date}", "{localisation}", "{house}", "{seller}", "{url_full_detail}", "{auction_title}", "{item_title}", "{detailed_title}", "{item_description}", "{detailed_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{is_item_result}", "{currency}"  
FROM "{christies_name}" )
UNION ALL
(SELECT DISTINCT "{id_item}", "{id_picture}", "{lot}", "{date}", "{localisation}", "{house}", "{seller}", "{url_full_detail}", "{auction_title}", "{item_title}", "{detailed_title}", "{item_description}", "{detailed_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{is_item_result}", "{currency}"   
FROM "{sothebys_name}")
