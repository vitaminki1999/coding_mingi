import serial
import socket
import pymysql
import datetime

serial_port = '/dev/ttyS0'
baud_rate = 9600

# 시리얼 포트 초기화
ser = serial.Serial(serial_port, baud_rate)
# database 주소
host = 'svc.sel5.cloudtype.app'
port = 32712
user = 'root'
password = '2024320319'
database = 'new_schema'
charset = 'utf8mb4'

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 7070))  # 서버 소켓을 모든 네트워크 인터페이스에 바인딩
server_socket.listen(1)  # 최대 1개의 클라이언트 연결을 허용

print("서버 대기 중...")

while True:
    # 클라이언트 연결 대기
    client_socket, client_address = server_socket.accept()
    print(f"클라이언트가 연결되었습니다: {client_address}")

    try:
        while True:
            if ser.in_waiting > 0:
                received_data = ser.readline().decode().strip()
                if received_data.startswith('T'):
                    temperature_str = received_data.split('=')[1]
                    temperature = float(temperature_str)
                    # 온도 값을 클라이언트에게 전송
                    print(f"Received temperaure: {temperature:.2f}")
                    client_socket.sendall(f'Temperature: {temperature}\n'.encode())
                    try:
                        dbtest = pymysql.connect(
                            host=host,
                            port=port,
                            user=user,
                            password=password,
                            database=database,
                            charset=charset,
                            cursorclass=pymysql.cursors.DictCursor
                        )
                        print('MySQL 서버에 성공적으로 연결되었습니다.')

                        cursor = dbtest.cursor()
                        float_data = temperature
               
                        now=datetime.datetime.now()+datetime.timedelta(hours=8)
               
                        cursor.execute('INSERT INTO new_table2 (temperatur, time) VALUES (%s, %s)', (float_data, now))
                        dbtest.commit()
                    except pymysql.Error as e:
                        print(f'MySQL 서버에 연결할 수 없습니다: {e}')
                    finally:
                        if 'dbtest' in locals() and dbtest.open:
                            dbtest.close()
                            print('MySQL 서버 연결이 닫혔습니다.')
                           
               
           
    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
       
       
        client_socket.close()
