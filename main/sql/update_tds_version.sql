UPDATE {schema_name}.{tds_version_table}
  SET csv_hash = '{csv_hash}'
  WHERE
    file_name = '{file_name}'
    AND table_name = '{table_name}'
    AND csv_hash <> '{csv_hash}'
;
