-- Deduplication for ERP and Liaison files
CREATE TABLE erp_clean AS
SELECT DISTINCT * FROM read_excel_auto('{{workingDir}}/data/Fichier_erp.xlsx')
WHERE product_id IS NOT NULL;

CREATE TABLE liaison_clean AS
SELECT DISTINCT * FROM read_excel_auto('{{workingDir}}/data/fichier_liaison.xlsx');

-- Cleaning and deduplicating the Web file
CREATE TABLE web_clean AS
SELECT DISTINCT * FROM read_excel_auto('{{workingDir}}/data/Fichier_web.xlsx')
WHERE sku IS NOT NULL AND post_title IS NOT NULL;

-- Merging the data
CREATE TABLE final_merge AS
SELECT 
  w.sku,
  w.post_title,
  l.product_id,
  e.price AS erp_price,
  w.total_sales AS web_sales,
FROM web_clean w
LEFT JOIN liaison_clean l ON w.sku = l.id_web
LEFT JOIN erp_clean e ON l.product_id = e.product_id;

-- Dropping the id_web column if not needed
ALTER TABLE final_merge DROP COLUMN id_web;

-- Calculating total revenue (CA) per product
SELECT 
  post_title AS product_name, 
  SUM(erp_price * web_sales) AS CA
FROM final_merge
GROUP BY post_title
ORDER BY CA DESC;
