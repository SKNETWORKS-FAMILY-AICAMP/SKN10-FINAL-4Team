<div align="center">
   
# LUMINA.
**AI 인플루언서 챗봇 플랫폼**

</div>

<div align="center">
<!-- <img width="700" height="300" src="https://github.com/user-attachments/assets/6e4ead57-5ec5-49c7-8d72-d9c7b0762392"/>-->
   
![Screenshot_2025-06-11_at_3 29 37_PM-removebg-preview](https://github.com/user-attachments/assets/2a09f271-ffa7-4ce9-a896-bfa1bb36ee96)
![seyeon-removebg-preview](https://github.com/user-attachments/assets/babb77ea-f2f4-4725-81b5-046a0f3c8782)

<!-- <img width="350" height="350" src="https://github.com/user-attachments/assets/e536447a-a6b9-452f-b110-02281e833eee"/> -->
<!-- <img width="330" height="330" src="https://github.com/user-attachments/assets/31d15df3-f0ea-4725-98d2-5bdb89047a13"/>
 -->
</div>

<div align="center">
   
![Screenshot 2025-06-11 at 11 29 22 AM](https://github.com/user-attachments/assets/3fd385ab-c148-4c77-acf5-9b4393d59b9d)

## Team Goodfellow

| ![Hyeonjoon](https://github.com/hyeonjoonpark.png?size=100) | ![Alice](https://github.com/hyeonjoonpark.png?size=100) | ![Jin](https://github.com/hyeonjoonpark.png?size=100) | ![Sara](https://github.com/hyeonjoonpark.png?size=100) | ![Sara](https://github.com/hyeonjoonpark.png?size=100) | ![Sara](https://github.com/hyeonjoonpark.png?size=100)
|:--:|:--:|:--:|:--:|:--:|:--:|
| **이종원**<br/>Product Manger | **박현준**<br/>Voice AI Developer | **김재혁**<br/>LLM Developer | **전서빈**<br/>Data Engineer | **편성민**<br/>Data Engineer | **조영훈**<br/>Data Engineer |
</div>

<br/>
<br/>


## About LUMINA.
**루미나(Lumina)**_는 인플루언서와의 개인화된 소통 경험을 제공하는 감성 AI 플랫폼입니다.
실제 인플루언서의 말투, 억양, 보이스 스타일을 정밀하게 클로닝하여, 사용자가 마치 진짜 인플루언서와 직접 대화하는 듯한 몰입감과 정서적 연결감을 제공합니다. 루미나는 단순한 챗봇을 넘어, 팬과 인플루언서 사이의 심리적 거리감을 줄이고, 새로운 형태의 소통 문화를 제시합니다._

<br/>
<br/>

![Screen Recording 2025-07-10 at 8 34 55 PM (1)](https://github.com/user-attachments/assets/9dd1b50e-3bd1-4123-a905-ba7a27ec7597)


<br/>
<br/>

## Features

###  말투 및 어투 완벽 재현  
인플루언서 특유의 말버릇, 억양, 화법을 정밀하게 복원하여  
실제와 유사한 자연스러운 대화 경험을 제공합니다.

###  실제 음성과 톤 클로닝  
감정, 발음, 억양까지 반영된 고품질 음성 합성을 통해  
마치 실제 인플루언서와 통화하는 듯한 몰입감을 제공합니다.

###  성격과 반응 패턴 반영  
인플루언서의 성격, 유머 코드, 감정 반응을 학습하여  
상황에 맞는 개성 있는 맞춤형 응답을 생성합니다.

## 서비스 구조
![Screenshot 2025-06-11 at 3 39 54 PM](https://github.com/user-attachments/assets/a8a45ca1-0dfb-4088-92c6-65f782712670)



## 텍스트 모델 발전 과정
<img src="https://github.com/user-attachments/assets/17d017de-1c85-469c-911e-1bc5b0c4807a" width="500" />

<img src="https://github.com/user-attachments/assets/01474372-cb88-47ed-8132-0065a9f9fcca" width="500" />

## 보이스 모델 발전 과정

### 코사인 유사도 (벡터)
![image](https://github.com/user-attachments/assets/fe28b9ac-a14a-49ed-a10a-fbdea709d3f1)

### PCA / t-SNE (차원 축소)
![image](https://github.com/user-attachments/assets/874a0750-3eba-4184-b9a2-121d43c82798)

### 3D 시각화
![image](https://github.com/user-attachments/assets/d5fcfbdf-6275-47c9-aa66-0049ae7d633d)

### MFCC (FFT 음성 특징 유사도)
![image](https://github.com/user-attachments/assets/39afb28a-dc05-4955-b565-1cb15207f747)


## 인플루언서 자동 생성 파이프라인 및 검증
#### 인플루언서 생성 과정은 많은 수작업을 요합니다. 관리자들의 권한으로, 인플루언서 생성 과정을 다수의 유튜브 url, 이름 및 이미지로 한번에 생성하는 시스템을 구축하였습니다. 
<img width="2560" height="991" alt="Screenshot 2025-07-10 at 8 18 07 PM" src="https://github.com/user-attachments/assets/98dc37ab-b869-4afe-928b-1a266aca7172" />

#### 인플루언서 생성은 파인튜닝 과정이 필요하기 때문에 일정 시간 이후 준비가 완료되면 활성화됩니다.
<img width="441" height="259" alt="Screenshot 2025-07-10 at 8 55 21 PM" src="https://github.com/user-attachments/assets/05c28f71-528e-460f-9b92-a95d82fceff6" />

#### 정의된 파라미터로 시스템 프롬프팅, 말투 모델 파인튜닝, 음성 모델 파인튜닝을 성공적으로 수행합니다. 
<img width="1373" height="608" alt="Screenshot 2025-07-10 at 8 20 03 PM" src="https://github.com/user-attachments/assets/f157cd20-29fc-453a-a625-2f3eb788da35" />

#### 자동 생성 파이프라인은 다중 유튜브 링크를 모두 파인튜닝해 분석하며, 최고의 성능을 기록한 모델을 선정해 인플루언서를 생성하며, 수동 생성 파이프라인 대비 뒤쳐지지 않는 수준을 보입니다.
<img width="455" height="258" alt="Screenshot 2025-06-19 at 8 06 00 PM" src="https://github.com/user-attachments/assets/e31a4532-3336-4b3b-82d6-bbbb5991aee2" />
<img width="5967" height="2365" alt="audio_similarity_spatial" src="https://github.com/user-attachments/assets/ead8b664-d46d-4499-8167-1e6d3d1512f3" />

## 관리자 페이지
#### 본 서비스는 SKN 수강생들을 대상으로 배포되었습니다. 효율적인 모니터링과 데이터를 습득하기 위한 관리자 페이지를 지원합니다. 
<img width="1237" height="424" alt="Screenshot 2025-07-10 at 8 28 23 PM" src="https://github.com/user-attachments/assets/7c9dc801-b152-4219-aa55-9364c2fccac8" />
<img width="1244" height="495" alt="Screenshot 2025-07-10 at 8 28 51 PM" src="https://github.com/user-attachments/assets/9ede4905-337b-4a49-9c31-bff57f698650" />

## 배포
#### AWS Elasticbeanstalk을 활용하여 빠른 배포를 수행했습니다. HTTPS 와 커스텀 도메인을 지원하며, 로드 밸런싱을 통한 트래픽 관리를 수행합니다. 트래픽은 수요에 따라 1-4 인스턴스로 유동적으로 스케일링합니다. 
<img width="1349" height="845" alt="Screenshot 2025-07-10 at 8 24 38 PM" src="https://github.com/user-attachments/assets/44c5e353-3898-4f89-aecd-5dfd0db2b822" />

## Skills

#### Languages & Syntax:

[![My Skills](https://skillicons.dev/icons?i=python,linux)](https://skillicons.dev)


#### Frontend Development:
[![My Skills](https://skillicons.dev/icons?i=html,css,js,figma)](https://skillicons.dev)

#### Backend & Frameworks:
[![My Skills](https://skillicons.dev/icons?i=django,ubuntu)](https://skillicons.dev)

#### Deployment & Cloud Services:
[![My Skills](https://skillicons.dev/icons?i=aws)](https://skillicons.dev)

#### Aritificial Intelligence & Data
[![My Skills](https://skillicons.dev/icons?i=pytorch,sklearn)](https://skillicons.dev)
<img src="https://github.com/user-attachments/assets/33f61e6b-e7f2-4629-924a-d9e0c83654d3" width="50" />
<img src="https://github.com/user-attachments/assets/6e036d43-461d-4642-b5b5-4771143bd2ec" width="50" />
<img src="https://github.com/user-attachments/assets/831b1873-9d40-401f-8202-9fe4e814a17a" width="50" />


#### Database Management:
[![My Skills](https://skillicons.dev/icons?i=aws,postgres)](https://skillicons.dev)


#### Development Tools:
[![My Skills](https://skillicons.dev/icons?i=git,github,postman,discord)](https://skillicons.dev)

#### Development Environments:
[![My Skills](https://skillicons.dev/icons?i=vscode)](https://skillicons.dev)
<img src="https://github.com/user-attachments/assets/8d4d3434-7c57-4633-a3be-cb638abb4565" width="50" />


<br>
<br>



## Setup
1. 리포지토리 클론:
   ```sh
   git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN10-FINAL-4Team.git
   cd goodfellow
   ```
2. 가상환경 생성 및 활성화:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
3. 필수 라이브러리 설치:
   ```sh
   pip install -r requirements.txt
   ```
4. 환경변수 `.env` 생성.
5. 마이크레이션:
   ```sh
   python manage.py migrate
   ```
6. 로컬 서버 실행:
   ```sh
   python manage.py runserver
   ```

## 환경변수
프로젝트 루트 디렉토리에 `.env` 파일 생성:
```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
```

## 프로젝트 실행
- 브라우저에서 `http://localhost:8000` 방문.
- 구글 로그인 후 인플루언서들과 대화.

## License
MIT License
