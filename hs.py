from selenium import webdriver
from email.mime.text import MIMEText
import chromedriver_autoinstaller
import time
import threading
import datetime
import smtplib


#-----------------------------------개인설정-----------------------------------------

#한신대 포털 로그인 정보
ID = "아이디 입력"
PW = "비밀번호 입력"

#갱신 딜레이 설정 (초)
delay = 150

#전송용 Gmail
send_m = "Gmail 입력"
send_p = "비밀번호 입력" #앱 비밀번호

#알림받을 메일
receive_m = "메일 입력"

#----------------------------------------------------------------------------------

print("========[한신대학교 비교과 목록 크롤러]========")
time.sleep(0.5)

#hs_data 초기화
f = open("hs_data.txt", 'w')
f.close()


def write_data(data):

    f = open("hs_data.txt", 'w', encoding='UTF-8')
    f.write(data)
    f.close()


def crawler():
   
    
    
    main_url = 'https://portal.hs.ac.kr/html/main/index.html?app=noncurriculum&menu=03030000'

    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  #크롬드라이버 버전 확인

    options = webdriver.ChromeOptions() #크롬드라이버 옵션
    options.add_argument("headless") #창없이 실행

    try:
        print("\n크롬드라이버 체크...")
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=options)
    
    except:
        print("크롬드라이버 자동 설치...")
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=options)
    
    print("접속중...")
    driver.implicitly_wait(30)

    driver.get(main_url)

    print("로그인중...")
    driver.implicitly_wait(30)

    #자동 로그인
    ID_box = driver.find_element_by_css_selector('#userId')
    PW_box = driver.find_element_by_css_selector('#userPwd')

    ID_box.send_keys(ID)
    PW_box.send_keys(PW)

    login_bt = driver.find_element_by_css_selector('#ssoLoginFrm > div.idLoginBox > div > input[type=submit]:nth-child(3)')

    login_bt.click()
    print("로그인 완료")
    print("접속중...")
    driver.implicitly_wait(30)

    #비교과 신청 페이지로 이동
    driver.get(main_url)

    driver.implicitly_wait(30)

    print("크롤링...\n")
    #페이지 개수 크롤
    pages = driver.find_elements_by_css_selector("#tab0 > div.paginate > span > a")

    last_page = int(pages[-1].text)


    driver.implicitly_wait(30)


    #페이지 넘겨가면서 크롤
    L1 = []
    L2 = []
    dic = {}
    
    page_num = 1
    
    while page_num <= last_page:
    
        print(f"{page_num} 페이지 크롤링...\n")
    
        driver.implicitly_wait(30)
    
        #비교과 프로그램 제목, 인원 크롤
        content = driver.find_elements_by_css_selector("#ncuPgmGaeseolListLoading > div:nth-child(n) > div.list-content > span.cont-tit")
        num = driver.find_elements_by_css_selector("#ncuPgmGaeseolListLoading > div:nth-child(n) > div.list-content > span.etc.icon-users") #리스트
        
        #텍스트만 뽑아내서 새로운 리스트 생성
        for i in content:
            t = i.text
            L1.append(t)
        
        for i in num:
            t = i.text
            L2.append(t)
        
    
        #다음페이지로 넘기기
        driver.implicitly_wait(30)
        next_bt = driver.find_element_by_css_selector("#tab0 > div.paginate > a.next > span")
        driver.execute_script("arguments[0].click();", next_bt)

        page_num += 1

        time.sleep(1)
    
    now_data = "\n".join(L1)
    
    #제목, 인원 딕셔너리
    dic = dict(zip(L1,L2)) #아직 미사용


    full_text = ""
    for L1, L2 in zip(L1, L2):
        full_text += f"제목 : {L1}\n인원 : {L2}\n\n"

    print(full_text)
   
    
    #메일 본문 내용
    full_mes = f"{full_text}\n[비교과 바로가기]\n{main_url}"
    
   
    f = open("hs_data.txt", 'r', encoding='UTF-8')
    old_data = f.read()
    f.close()
    
    
    if old_data != now_data:
        print("====[새로운 비교과 내용을 확인했습니다]====")
        
        
        # 세션 생성
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # TLS 보안 시작
        s.starttls()
        
        # 로그인 인증
        s.login(f'{send_m}', f'{send_p}')
        
        # 보낼 메시지 설정
        msg = MIMEText(f'\n\n{full_mes}')
        msg['Subject'] = '한신대 비교과 갱신 알림'
        
        # 메일 보내기
        s.sendmail(f"{send_m}", f"{receive_m}", msg.as_string())
            
        # 세션 종료
        s.quit()
        
        print("\n메일 전송 완료")
        
        
    else:
        print("=====[새로운 비교과 내용이 없습니다]=====")
    
    
    #이번 데이터 저장
    write_data(now_data)
    
    driver.quit()
    
    
    print("크롤링 완료\n")
    
    now = datetime.datetime.now()
    print(now.strftime('=================%Y-%m-%d=================\n===============%H시 %M분 %S초===============\n')) #현재 시간
    
    print(f"============{delay}초 후 갱신됩니다.============\n\n\n")
    
    
    
    threading.Timer(delay, crawler).start() #delay마다 크롤
    

crawler()
