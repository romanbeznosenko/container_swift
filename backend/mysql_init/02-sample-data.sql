INSERT INTO swift_codes (swiftCode, address, countryISO2, countryName, isHeadquarter)
SELECT * FROM (
    SELECT 'DEUTDEFF' as swiftCode, 'Taunusanlage 12, 60325 Frankfurt am Main' as address, 'DE' as countryISO2, 'Germany' as countryName, 0 as isHeadquarter
    UNION ALL
    SELECT 'DEUTDEFFXXX', 'Taunusanlage 12, 60325 Frankfurt am Main', 'DE', 'Germany', 1
    UNION ALL
    SELECT 'CHASUS33', '270 Park Avenue, New York', 'US', 'United States', 0
    UNION ALL
    SELECT 'CHASJPJT', 'Tokyo Building, 2-7-3, Marunouchi, Chiyoda-ku', 'JP', 'Japan', 0
) AS temp
WHERE NOT EXISTS (
    SELECT 1 FROM swift_codes LIMIT 1
);