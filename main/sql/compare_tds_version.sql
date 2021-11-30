SELECT
  table_name, file_name
FROM
  {schema_name}.{tds_version_table}
WHERE
  file_name =  '{file_name}'
  AND table_name = '{table_name}'
  AND csv_hash <> '{csv_hash}'
;
