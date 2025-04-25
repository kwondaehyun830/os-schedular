OS Scheduler Project

이 프로젝트는 Python Flask와 pywebview를 이용한 멀티코어 FCFS 스케줄러 시뮬레이터입니다.

디렉터리 구조

/ (프로젝트 루트)
├── os_app.py            # Flask 서버 및 pywebview 창 생성 엔트리포인트
├── scheduler.py         # FCFS 스케줄링 알고리즘 구현 (fcfs_schedule_multi)
├── requirements.txt     # Python 의존 패키지 목록 (flask, pywebview 등)
├── .gitignore           # Git에서 제외할 파일/디렉터리 패턴
└── static/              # 프론트엔드 정적 파일 폴더
    ├── index.html       # 메인 HTML 페이지
    ├── app.js           # 클라이언트 측 JS: 입력 처리, Gantt 차트 렌더링, 애니메이션
    └── style.css        # (선택) 차트 및 UI 스타일 정의

주요 파일 설명

os_app.py

Flask 앱을 실행하고, /api/fcfs 엔드포인트를 통해 프로세스 데이터를 받아 스케줄링 결과를 반환합니다.

pywebview를 사용해 데스크탑 GUI 창으로 인코딩된 웹 UI를 띄웁니다.

scheduler.py

fcfs_schedule_multi(processes, cores) 함수 구현부가 들어 있습니다.

Process 목록과 P/E 코어 구성 정보를 받아 First-Come-First-Serve 스케줄링을 수행하고 결과를 리턴합니다.

static/index.html

입력 폼(프로세스 수, 도착/서비스 시간, P/E 코어 설정)과 결과를 볼 수 있는 Gantt 차트를 정의한 HTML 문서입니다.

static/app.js

DOMContentLoaded 이벤트로 버튼 클릭 핸들러(genFields, runFCFS)를 등록합니다.

/api/fcfs 호출 후 스케쥴 결과로 Gantt 차트를 그리고, marker 애니메이션을 실행합니다.

static/style.css

차트 및 버튼, 입력창 등의 기본 스타일을 정의합니다.

requirements.txt

Flask
pywebview

pip install -r requirements.txt로 필요한 패키지를 한 번에 설치할 수 있습니다.

실행 방법

의존성 설치

pip install -r requirements.txt

앱 실행

python os_app.py

GUI 창이 열리면 프로세스 수, 도착/서비스 시간, P/E 코어 수 등을 입력하고 스케줄러를 실행하세요.

본 README는 프로젝트의 전체 구조와 각 파일의 역할을 한눈에 파악할 수 있도록 작성되었습니다.

