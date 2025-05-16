-- Deduplication for ERP and Liaison files

CREATE TABLE erp_clean AS
SELECT DISTINCT ON (product_id) * 
FROM read_xlsx('{{workingDir}}/data/Fichier_erp.xlsx', all_varchar = true)
WHERE product_id IS NOT NULL;

CREATE TABLE liaison_clean AS
SELECT DISTINCT ON (product_id, id_web) * 
FROM read_xlsx('{{workingDir}}/data/fichier_liaison.xlsx', all_varchar = true);

CREATE TABLE web_clean AS
SELECT DISTINCT ON (sku) * 
FROM read_xlsx('{{workingDir}}/data/Fichier_web.xlsx', all_varchar = true)
WHERE sku IS NOT NULL AND post_title IS NOT NULL;

CREATE TABLE final_merge AS
SELECT 
w.sku,
w.post_title AS product_name,
l.product_id,
CAST(e.price AS DOUBLE) AS price,
CAST(w.total_sales AS INTEGER) AS sales,
CAST(e.price AS DOUBLE) * CAST(sales AS INTEGER) AS CA
FROM web_clean w
LEFT JOIN liaison_clean l ON w.sku = l.id_web
LEFT JOIN erp_clean e ON l.product_id = e.product_id;

COPY final_merge TO '{{workingDir}}/output/final_merge.csv' (HEADER, DELIMITER ',');
