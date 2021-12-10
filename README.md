# TABDANC (Table Data Sync)

Tabdanc is a library that maintain and manage latest data.

Main Feature compares the .csv data stored in the database with the .csv file in local repository and if they are different, update the table with the latest data. (In this case, the latest data is the data in local repository)

Local repository must exist files, .csv, .meta, .td. <br>
(If any of the three files is not exist, it will not be updated)

- `.csv`: .csv file is the data file you want to maintain and manage.
- `.meta`: .meta file is a json file in which the table name where the csv should be saved is written.
  - .meta file name must be the same as the .csv file name
  ```json
  {
    "table_name": "table_name"
  }
  ```
- `.td`: .td file is a json file in which table schema definitions(column name, coulmn type) are written. 
  - .td file name must be the same as the table name
  - The column name of the .td file must be the same as the header name of the .csv file
  ```json
  {
    "columns": [
      {
        "name": "column_name1",
        "type": "int4"
      },
      {
        "name": "column_name2",
        "type": "varchar(255)"
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
$ pip install tabdanc
```

## Usage

### Command Help

```sh
# help tabdanc command
$ tabdanc -h
```

### Config Settings

First, you need to set config to use tabdanc 

```sh
# help
$ tabdanc config -h

# create config file 
$ tabdanc config --create

# show config information
$ tabdanc config --list

# update config file
$ tabdanc config --update {section.option} {value}
```

### Table Update

You can use the update command to add the csv file to your database. <br>
If the csv file stored in the database is changed, the changed csv file is updated to the database using the update command.

```sh
# help
$ tabdanc update -h

# update table
$ tabdanc update
```

### File Upload / Download

> When upload or download through the '-f' option, enter only the file name without the extension. <br> When enter upload or download command, files related to the file name are upload or download. ex) .csv .meta .td

#### Upload

If you use the upload command, you can upload files from the local repository to the remote repository.

```sh
# help
$ tabdanc upload -h

# upload all files
$ tabdanc upload -a

# upload one file
$ tabdanc upload -f file_name

# upload multiple files
$ tabdanc upload -f file_name1 file_name2
```

#### Download

If you use the download command, you can download files from the remote repository to the local repository.

```sh
# help
$ tabdanc download -h

# download all files
$ tabdanc download -a

# download one file
$ tabdanc download -f file_name

# download multiple files
$ tabdanc download -f file_name1 file_name2
```

## Contact

- Chae JungWoo - jungwoo@linewalks.com
- Lee Yuna - una944@linewalks.com
- Choi Insu - insu@linewalks.com
