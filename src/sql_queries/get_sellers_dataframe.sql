(SELECT DISTINCT "{id_unique}", "{id_item}", "{id_picture}", "{url_full_detail}", "{url_auction}", "{lot}", "{date}", "{localisation}", "{type_sale}", "{seller}", "{house}", "{auction_title}", "{detailed_title}", "{total_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{currency}", "{is_item_result}", "{is_picture}"  
FROM "{drouot_name}")
UNION ALL
(SELECT DISTINCT "{id_unique}", "{id_item}", "{id_picture}", "{url_full_detail}", "{url_auction}", "{lot}", "{date}", "{localisation}", "{type_sale}", "{seller}", "{house}", "{auction_title}", "{detailed_title}", "{total_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{currency}", "{is_item_result}", "{is_picture}"
FROM "{christies_name}" )
UNION ALL
(SELECT DISTINCT "{id_unique}", "{id_item}", "{id_picture}", "{url_full_detail}", "{url_auction}", "{lot}", "{date}", "{localisation}", "{type_sale}", "{seller}", "{house}", "{auction_title}", "{detailed_title}", "{total_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{currency}", "{is_item_result}", "{is_picture}"  
FROM "{sothebys_name}")
UNION ALL
(SELECT DISTINCT "{id_unique}", "{id_item}", "{id_picture}", "{url_full_detail}", "{url_auction}", "{lot}", "{date}", "{localisation}", "{type_sale}", "{seller}", "{house}", "{auction_title}", "{detailed_title}", "{total_description}", "{min_estimate}", "{max_estimate}", "{item_result}", "{currency}", "{is_item_result}", "{is_picture}" 
FROM "{millon_name}")