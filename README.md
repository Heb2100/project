<div style="text-align: center;">
    <h1 style="font-size: 24px; font-weight: bold;">1. 소개 및 수행업무</h1>
    <p style="font-size: 18px;">KOSPI 상한가 스크래퍼 사용 예제</p>
    <p style="font-size: 16px;">본 스크래퍼는 KOSPI 시장에서 상한가 종목을 자동으로 수집하고, 핵심 정보를 요약하여 전달하는 기능을 수행합니다.</p>
    <p style="font-size: 16px;">처음에는 친구의 요청으로 개발을 시작했지만, 점차 그의 직장 동료들까지 유용하게 활용하며 업무 효율성을 높이는 데 기여했습니다.</p>
    <div style="display: flex; justify-content: center; gap: 10px;">
        <img src="https://github.com/user-attachments/assets/9e5c1651-dfa5-4cf2-a1e9-2c0530df9366" 
             alt="Image 1" style="width: 35%;">
        <img src="https://github.com/user-attachments/assets/fddd65b1-ba52-4296-bde4-65cd0fd6a1b4" 
             alt="Image 2" style="width: 35%;">
    </div>
</div>

<div style="text-align: center; margin-top: 30px;">
    <h1 style="font-size: 24px; font-weight: bold;">2. 트러블슈팅</h1>
    <p style="font-size: 18px;">스크래핑 과정에서 발생한 문제와 해결 방법</p>
    
    <p style="font-size: 16px;">구글이 스크래핑을 방어하기 위해 클래스를 난수로 변경</p>
    <p style="font-size: 16px;">초기에는 웹사이트의 HTML을 직접 분석하여 데이터를 추출하려 했으나, 
        구글은 자동화된 스크래핑을 방지하기 위해 CSS 클래스를 매 요청마다 난수로 변경하는 전략을 사용했습니다.</p>
    <p style="font-size: 16px;">이로 인해 기존 방식으로는 원하는 데이터를 안정적으로 수집할 수 없었으며, 
        해결책으로 <b>Google Custom Search API</b>를 활용하여 데이터를 수집하는 방향으로 전환했습니다.</p>
    
    <p style="font-size: 16px;"><b>웹사이트 구조 변경으로 인해 데이터 수집 불가</b></p>
    <p style="font-size: 16px;">사이트의 레이아웃이 변경되면서 기존의 XPath 및 CSS Selector 기반의 크롤러가 정상적으로 작동하지 않는 문제가 발생했습니다.</p>
    <p style="font-size: 16px;">이를 해결하기 위해 <b>BeautifulSoup</b>과 <b>Selenium</b>을 활용하여 동적인 CSS 선택자를 적용하고, 크롤링 전략을 유연하게 변경하였습니다.</p>
    
    <p style="font-size: 16px;"><b>요청 차단 문제</b></p>
    <p style="font-size: 16px;">짧은 시간 내에 다량의 요청을 보낼 경우, 서버에서 봇으로 인식하여 차단하는 문제가 발생했습니다.</p>
    <p style="font-size: 16px;">이를 방지하기 위해 <b>User-Agent</b>를 변경하고, 요청 간격을 랜덤하게 설정하여 서버 차단을 우회했습니다.</p>
</div>

<div style="text-align: center; margin-top: 30px;">
    <h1 style="font-size: 24px; font-weight: bold;">3. 기술 스택</h1>
    <p style="font-size: 18px;">이 프로젝트에서 사용한 기술들</p>
    <ul style="font-size: 16px; list-style-position: inside; text-align: left; display: inline-block; text-align: left;">
        <li><b>프로그래밍 언어</b>: Python</li>
        <li><b>웹 스크래핑</b>: Google Custom Search API, BeautifulSoup, Selenium</li>
        <li><b>데이터 처리</b>: Pandas</li>
        <li><b>데이터 저장</b>: CSV, SQLite</li>
        <li><b>배포 환경</b>: AWS Lambda (자동 실행)</li>
    </ul>
</div>
