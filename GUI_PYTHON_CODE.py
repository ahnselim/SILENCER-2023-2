import tkinter as tk
import serial
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 아두이노가 연결된 포트와 보레이트 설정
ser = serial.Serial('COM12', 115200)

# GUI 업데이트를 위한 큐 생성
q = queue.Queue()

# 데이터를 저장할 리스트 생성
decibel1_data = []
decibel2_data = []

# 그래프를 그릴 figure 생성
fig, ax = plt.subplots()


# 그래프를 그리는 함수
def draw_graph():
    ax.clear()  # 그래프 초기화
    ax.plot(decibel1_data, label='Mic1')  # 첫 번째 마이크 데이터 그래프 그리기
    ax.plot(decibel2_data, label='Mic2')  # 두 번째 마이크 데이터 그래프 그리기
    ax.set_xlabel('Time (s)')  # x축 레이블 설정
    ax.set_ylabel('Decibel (dB)')  # y축 레이블 설정
    ax.legend()  # 범례 표시
    fig.canvas.draw()  # 그래프 갱신

def read_serial():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', 'ignore').rstrip()
            q.put(line)  # 큐에 라인 추가

def send_command(command):
    ser.write(str(command).encode('utf-8'))

def update_gui():
    while not q.empty():
        line = q.get()  # 큐에서 라인 추출
        if line.startswith("Frequency : "):
            frequency = line.split(": ")[1].split(" ")[0]  # 주파수 값 추출
            label_freq.config(text=f"Frequency: {frequency} Hz")  # 주파수 라벨 업데이트
        elif line.startswith("Sound Level Mic1 (dB): "):
            decibel1 = line.split(": ")[1]  # 첫 번째 마이크 값 추출
            label1.config(text=f"Sound Level Mic1 (dB): {decibel1} ")  # 라벨1 업데이트
            decibel1_data.append(float(decibel1))  # 데이터 저장
        elif line.startswith("Sound Level Mic2 (dB): "):
            decibel2 = line.split(": ")[1]  # 두 번째 마이크 값 추출
            label2.config(text=f"Sound Level Mic2 (dB): {decibel2} ")  # 라벨2 업데이트
            decibel2_data.append(float(decibel2))  # 데이터 저장
        elif line.startswith("Decibel reduction (dB) : "):
            decibel3 = line.split(": ")[1]  # 데시벨 감소량 값 추출
            label_reduct.config(text=f"Decibel reduction (dB): {decibel3} ")  # 데시벨 감소량 라벨 업데이트
        elif line.startswith("distance"):
            distance = line.split(": ")[1]  # 거리 값 추출
            label_distance.config(text=f"Distance: {distance} cm")  # 거리 라벨 업데이트
        elif line.startswith("diskdistance : "):
            diskdis = line.split(": ")[1]  # 디스크 거리 값 추출
            label_diskdistance.config(text=f"diskistance: {diskdis} cm")  # 디스크 거리 라벨 업데이트
        
        

    draw_graph()  # 그래프 그리기

    root.after(100, update_gui)  # 100ms 후에 update_gui 함수 재호출

# GUI 생성
root = tk.Tk()
root.config(bg='light yellow')  # GUI 배경색을 연노랑색(light yellow)으로 설정
root.title("Arduino Sound Level Monitor")

# 그래프를 표시할 캔버스 생성
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=0, rowspan=20)  # rowspan 파라미터로 그래프가 여러 행을 차지하도록 설정

# Toggle Mode를 관리하는 변수 생성
toggle_mode = False

def toggle_command():
    global toggle_mode
    # Toggle 상태 변경
    toggle_mode = not toggle_mode
    send_command(3)
    # Toggle 상태에 따라 버튼 색 변경
    if toggle_mode:
        button1.config(bg='#F08080')  # Toggle Mode가 활성화되면 빨간색으로 변경
    else:
        button1.config(bg='#BCF5A9')  # Toggle Mode가 비활성화되면 원래의 색으로 변경


# 라벨 생성
label_freq = tk.Label(root, text="Frequency: ",bg='#A9D0F5')
label_freq.grid(row=0, column=2)

label1 = tk.Label(root, text="Sound Level Mic1 (dB): ",bg='#A9D0F5')
label1.grid(row=2, column=2)

label2 = tk.Label(root, text="Sound Level Mic2 (dB): ",bg='#A9D0F5')
label2.grid(row=4, column=2)

label_reduct = tk.Label(root, text="Decibel reduction (dB): ",bg='#A9D0F5')
label_reduct.grid(row=6, column=2)

label_distance = tk.Label(root, text="Distance: ",bg='#A9D0F5')
label_distance.grid(row=8, column=2)

label_diskdistance = tk.Label(root, text="diskdistance: ",bg='#A9D0F5')
label_diskdistance.grid(row=10, column=2)





# 버튼 생성
button1 = tk.Button(root, text="Toggle Mode", bg='#BCF5A9', command=toggle_command)
button1.grid(row=12, column=2)

button2 = tk.Button(root, text="forward direction",bg='#BCF5A9', command=lambda: send_command(1))
button2.grid(row=14, column=2)

button3 = tk.Button(root, text="reverse direction",bg='#BCF5A9', command=lambda: send_command(0))
button3.grid(row=16, column=2)

button4 = tk.Button(root, text="STOP",bg='#BCF5A9', command=lambda: send_command(2))
button4.grid(row=18, column=2)



# 새로운 스레드에서 시리얼 통신 읽기 시작
threading.Thread(target=read_serial).start()

# GUI 업데이트 시작
update_gui()

root.mainloop()
