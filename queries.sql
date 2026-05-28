
SELECT
    country_code,
    country_name,
    currency_code,
    vat_rate,
    region
FROM countries
WHERE is_active = 1;

SELECT
    cr.category_name,
    cr.margin_rate,
    cr.strategic_flag,
    cr.default_channel_code,
    c.channel_name
FROM category_rules cr
JOIN channels c ON cr.default_channel_code = c.channel_code
WHERE cr.is_active = 1;


SELECT
    channel_code,
    channel_name,
    acquisition_cost_gbp,
    channel_group
FROM channels
WHERE is_active = 1;
