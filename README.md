# TABDANCE (Table Data Syncer)

Tabdance is a library that maintain and manage latest data.

Main Feature compares the .csv data stored in the database with the .csv file in local repository and if they are different, update the table with the latest data. (In this case, the latest data is the data in local repository)

Local repository must exist files, .csv, .meta, .td. <br>
(If any of the three files is not exist, it will not be updated)

- `.csv`: .csv file is the data file you want to maintain and manage.
- `.meta`: .meta file is a json file in which the table name where the csv should be saved is written.
  - .meta file name must be the same as the .csv file name
  - `column_match` is an optional value.
  Set `column_match` when csv header and table column are different.
  - An error occurs if the `csv_header` is not in the .csv file or the `table_column` is not in the .td file.
  ```json
  {
    "table_name": "table_name",
    "column_match": {
      "csv_header": "table_column",
      ...
    }
  }
  ```
- `.td`: .td file is a json file in which table schema definitions(column name, coulmn type) are written. 
  - .td file name must be the same as the table name
  ```json
  {
    "columns": [
      {
        "name": "column_name1",
        "type": "int4",
        "primary_key": true
      },
      {
        "name": "column_name2",
        "type": "varchar(255)",
        "primary_key": false // same as not declared primary_key
      },
      ...
    ]
  }
  ```

There is one .td file per table, and multiple .csv files can be entered in one table. In this case, .meta files are created as many as the number of .csv files, and one .td file is created.

Additional Feature is that data files can be uploaded and downloaded by ssh connection between local repository and remote repository.

## Getting Started

### Built With

- Python >= 3.8

### Installation

```sh
$ pip install tabdance
```

## Usage

### Command Help

```sh
# help tabdance command
$ tabdance -h
```

### Config Settings

First, you need to set config to use tabdance 

```sh
# help
$ tabdance config -h

# create config file 
$ tabdance config --create

# show config information
$ tabdance config --list

# update config file
$ tabdance config --update {section.option} {value}
```

### Table Update

You can use the update command to add the csv file to your database. <br>
If the csv file stored in the database is changed, the changed csv file is updated to the database using the update command.

```sh
# help
$ tabdance update -h

# update table
$ tabdance update
```

### File Upload / Download

> When upload or download through the '-f' option, enter only the file name without the extension. <br> When enter upload or download command, files related to the file name are upload or download. ex) .csv .meta .td

#### Upload

If you use the upload command, you can upload files from the local repository to the remote repository.

```sh
# help
$ tabdance upload -h

# upload all files
$ tabdance upload -a

# upload one file
$ tabdance upload -f file_name

# upload multiple files
$ tabdance upload -f file_name1 file_name2
```

#### Download

If you use the download command, you can download files from the remote repository to the local repository.

```sh
# help
$ tabdance download -h

# download all files
$ tabdance download -a

# download one file
$ tabdance download -f file_name

# download multiple files
$ tabdance download -f file_name1 file_name2
```

## Contact

- Chae JungWoo - jungwoo@linewalks.com
- Lee Yuna - una944@linewalks.com
- Choi Insu - insu@linewalks.com
