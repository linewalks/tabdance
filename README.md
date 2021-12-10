# TABDANC (Table Data Sync)

Tabdanc is a library that maintain and manage latest data needed within CLUE

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

### Table Update

You can use the update command to add the csv file to your DBMS. <br>
If the csv file stored in the DBMS is changed, the changed csv file is updated to the DBMS using the update command.

```sh
# help
$ tabdanc update -h

# update table
$ tabdanc update
```

## Contact

- Chae JungWoo - jungwoo@linewalks.com
- Lee Yuna - una944@linewalks.com
- Choi Insu - insu@linewalks.com