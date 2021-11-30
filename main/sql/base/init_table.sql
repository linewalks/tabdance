CREATE TABLE IF NOT EXISTS {schema_name}.{tds_version_table} (
    file_name   varchar(255) UNIQUE NOT NULL,
    table_name  varchar(255) NOT NULL,
    csv_hash    text UNIQUE NOT NULL
);
