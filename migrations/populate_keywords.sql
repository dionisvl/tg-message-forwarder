-- Populate excluded_keywords table with initial data
INSERT INTO excluded_keywords (keyword, created_at)
SELECT keyword, NOW()
FROM (
    VALUES 
        ('test test'),
        ('test test1')
) AS t(keyword)
WHERE NOT EXISTS (
    SELECT 1 FROM excluded_keywords WHERE excluded_keywords.keyword = t.keyword
);

-- Show total count
SELECT COUNT(*) as total_keywords FROM excluded_keywords;