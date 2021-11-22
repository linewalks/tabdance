# CLUE-Uploader
CLUE 기능 동작에 필요한 데이터를 최신 내역으로 유지 및 데이터 관리를 위한 프로젝트입니다.

## Getting Started

### Built With
- Python 3.8.6

### Installation
1. Clone the repo
2. Install Python packages
   ```sh
   $ pip install -r requirements.txt
   ```
3. Set config file(`main/dvm.default.cfg 참고`) 
   ```sh
   $ cp main/dvm.default.cfg main/dvm.cfg
   ```
   - 자세한 정보는 프로젝트 담당자에 문의

## Usage

### Change Directory
아래에 작성된 Upload/Download 명령어를 실행하기 위해 main 폴더로 이동합니다.
```sh
$ cd main
```

### 명령어 도움
```sh
# upload 명령어 도움
$ python upload.py -h

# download 명령어 도움
$ python download.py -h
```

### 파일 업로드
> '-f' 명령어를 통해 업로드를 진행할 시, 확장자를 제외한 파일명만 입력합니다. </br>
명령어 입력시 해당 파일명에 관련된 .csv .meta .td 파일이 모두 업로드 됩니다.

```sh
# 모든 파일 업로드
$ python upload.py -a

# 1개 파일 업로드
$ python upload.py -f file_name

# 여러 파일 업로드
$ python upload.py -f file_name1 file_name2
```

### 파일 다운로드
> '-f' 명령어를 통해 다운로드를 진행할 시, 확장자를 제외한 파일명만 입력합니다. </br>
명령어 입력시 해당 파일명에 관련된 .csv .meta .td 파일이 모두 다운로드 됩니다.

```sh
# 모든 파일 다운로드
$ python download.py -a

# 1개 파일 다운로드
$ python download.py -f file_name

# 여러 파일 다운로드
$ python download.py -f file_name1 file_name2
```
