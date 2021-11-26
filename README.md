# TDS (Table Data Sync)
CLUE 기능 동작에 필요한 데이터를 최신 내역으로 유지 및 데이터 관리를 위한 프로젝트입니다.

## Getting Started

### Built With
- Python 3.8.6

### Installation
1. Clone the repo
2. Install setup.py
   ```sh
   $ python setup.py install
   ```
3. Set config file(`main/tds.default.cfg 참고`) 
   ```sh
   $ cp main/tds.default.cfg main/tds.cfg
   ```
   - 자세한 정보는 프로젝트 담당자에 문의

## Usage

### 명령어 도움
```sh
# table data sync 명령어 도움
$ tds -h
```

### 파일 업로드
> '-f' 명령어를 통해 업로드를 진행할 시, 확장자를 제외한 파일명만 입력합니다. </br>
명령어 입력시 해당 파일명에 관련된 .csv .meta .td 파일이 모두 업로드 됩니다.

```sh
# 모든 파일 업로드
$ tds upload -a

# 1개 파일 업로드
$ tds upload -f file_name

# 여러 파일 업로드
$ tds upload -f file_name1 file_name2
```

### 파일 다운로드
> '-f' 명령어를 통해 다운로드를 진행할 시, 확장자를 제외한 파일명만 입력합니다. </br>
명령어 입력시 해당 파일명에 관련된 .csv .meta .td 파일이 모두 다운로드 됩니다.

```sh
# 모든 파일 다운로드
$ tds download -a

# 1개 파일 다운로드
$ tds download -f file_name

# 여러 파일 다운로드
$ tds download -f file_name1 file_name2
```

## Contact
- 채정우 - jungwoo@linewalks.com
- 이유나 - una944@linewalks.com
- 최인수 - insu@linewalks.com
