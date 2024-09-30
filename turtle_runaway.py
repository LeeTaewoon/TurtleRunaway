import tkinter as tk
import turtle, random

class RunawayGame:
    def __init__(self, canvas, runner, chaser, catch_radius=50):
        self.canvas = canvas
        self.runner = runner
        self.chaser = chaser
        self.catch_radius2 = catch_radius**2
        self.time_left = 60  # 1분 시간 제한
        self.catch_count = 0  # 잡힌 횟수 카운트
        self.runner_speed_doubled = False  # 30초 이후 속도 증가 확인용 플래그

        # 모양 리스트와 인덱스 초기화
        self.shapes = ["arrow", "turtle", "circle", "square", "triangle", "classic"]
        self.shape_index = 0

        # Initialize 'runner' and 'chaser'
        self.runner.shape(self.shapes[self.shape_index])  # runner의 모양을 리스트의 첫 번째 모양으로 설정
        self.runner.color('blue')
        self.runner.penup()

        self.chaser.shape('turtle')  # chaser의 모양을 설정
        self.chaser.color('green')  # 기본 색상은 초록색
        self.chaser.penup()

        # Instantiate another turtle for drawing
        self.drawer = turtle.RawTurtle(canvas)
        self.drawer.hideturtle()
        self.drawer.penup()

        # Create a separate turtle for the timer
        self.timer_drawer = turtle.RawTurtle(canvas)
        self.timer_drawer.hideturtle()
        self.timer_drawer.penup()

        # Create a separate turtle for the score display
        self.score_drawer = turtle.RawTurtle(canvas)
        self.score_drawer.hideturtle()
        self.score_drawer.penup()

        # Create a separate turtle for the "Turtle Speed Up!" message
        self.speed_message_drawer = turtle.RawTurtle(canvas)
        self.speed_message_drawer.hideturtle()
        self.speed_message_drawer.penup()

    def is_catched(self):
        p = self.runner.pos()
        q = self.chaser.pos()
        dx, dy = p[0] - q[0], p[1] - q[1]
        return dx**2 + dy**2 < self.catch_radius2

    def start(self, init_dist=400, ai_timer_msec=100):
        self.runner.setpos((-init_dist / 2, 0))
        self.runner.setheading(0)
        self.chaser.setpos((+init_dist / 2, 0))
        self.chaser.setheading(180)

        # 타이머 및 게임 시작
        self.ai_timer_msec = ai_timer_msec
        self.update_timer()  # Start the countdown timer
        self.canvas.ontimer(self.step, self.ai_timer_msec)

    def update_timer(self):
        # 타이머 전용 거북이로 타이머만 업데이트 (화면을 지우지 않음)
        self.timer_drawer.clear()  # 타이머만 지우고 새로 그리기
        self.timer_drawer.penup()
        self.timer_drawer.setpos(-260, 325)  # 타이머를 상단 중앙에 표시
        if self.time_left > 0:
            self.timer_drawer.write(f'Time left: {self.time_left} seconds', align="center", font=("Arial", 16, "bold"))
            
            # 30초가 지나면 runner의 속도를 두 배로 증가하고, "Speed Up!" 메시지 표시
            if self.time_left == 30 and not self.runner_speed_doubled:
                self.runner.step_move *= 3  # runner의 속도를 3배로 증가
                self.runner_speed_doubled = True  # 속도를 한 번만 증가시키도록 플래그 설정
                self.show_speed_up_message()

            self.time_left -= 1
            self.canvas.ontimer(self.update_timer, 1000)  # 매 1초마다 호출
        else:
            self.timer_drawer.clear()
            self.timer_drawer.penup()  # 펜을 들어 올려야 새로운 위치로 이동할 수 있음
            self.timer_drawer.setpos(0, 100)  # 여기에서 x, y 좌표를 설정 (원하는 위치로)
            self.timer_drawer.write(f'Time Over! Game Ended\nTotal Catches: {self.catch_count}', align="center", font=("Arial", 16, "bold"))
            self.canvas.ontimer(None, 0)  # 타이머 종료

    def show_speed_up_message(self):
        """ 'Speed Up!' 메시지를 표시한 뒤, 2초 후에 제거 """
        self.speed_message_drawer.clear()
        self.speed_message_drawer.penup()
        self.speed_message_drawer.setpos(0, 0)  # 메시지를 중앙에 표시
        self.speed_message_drawer.write("Speed Up!", align="center", font=("Arial", 24, "bold"))
        self.canvas.ontimer(self.clear_speed_up_message, 2000)  # 2초 후에 메시지 지우기

    def clear_speed_up_message(self):
        """ 'Speed Up!' 메시지 제거 """
        self.speed_message_drawer.clear()

    def random_position(self):
        """ 거북이를 랜덤한 위치로 이동시키는 함수 (700x700 캔버스 내에서) """
        x = random.randint(-350, 350)
        y = random.randint(-350, 350)
        return (x, y)

    def step(self):
        # 타이머가 남아 있는 동안 게임을 진행
        if self.time_left > 0:
            self.runner.run_ai(self.chaser.pos(), self.chaser.heading())
            self.chaser.run_ai(self.runner.pos(), self.runner.heading())

            # chaser와 runner가 700x700 캔버스를 벗어나지 않도록 위치 조정
            self.keep_in_bounds(self.chaser)
            self.reflect_runner()

            is_catched = self.is_catched()

            if is_catched:
                self.catch_count += 1  # 잡힌 횟수 카운트 증가
                self.update_score()  # 점수 갱신

                # 잡힌 후, 도망자만 랜덤한 위치로 이동 (chaser는 이동하지 않음)
                self.runner.setpos(self.random_position())
                self.keep_in_bounds(self.runner)  # 이동한 위치도 경계 안에 있게 조정

                # runner의 모양을 순서대로 변경
                self.shape_index = (self.shape_index + 1) % len(self.shapes)  # 인덱스를 순환
                self.runner.shape(self.shapes[self.shape_index])

            self.canvas.ontimer(self.step, self.ai_timer_msec)

    def update_score(self):
        """ 점수를 업데이트하여 화면에 표시 """
        self.score_drawer.clear()
        self.score_drawer.penup()
        self.score_drawer.setpos(-285, 305)  # 점수를 화면에 표시
        self.score_drawer.write(f'Catch Count: {self.catch_count}', align="center", font=("Arial", 16, "bold"))

    def keep_in_bounds(self, turtle):
        """ 주어진 거북이가 700x700 캔버스 내에서만 움직이도록 제한 """
        x, y = turtle.pos()
        # x 좌표가 -350보다 작으면 -350, 350보다 크면 350으로 제한
        if x < -350:
            turtle.setx(-350)
        elif x > 350:
            turtle.setx(350)

        # y 좌표가 -350보다 작으면 -350, 350보다 크면 350으로 제한
        if y < -350:
            turtle.sety(-350)
        elif y > 350:
            turtle.sety(350)

    def reflect_runner(self):
        """ runner가 경계에 부딪혔을 때 반사각에 따라 움직이도록 설정 """
        x, y = self.runner.pos()
        heading = self.runner.heading()

        # x 좌표에서 경계에 부딪혔을 경우
        if x <= -350 or x >= 350:
            heading = 180 - heading  # 입사각과 반사각: x축 경계를 기준으로 반사

        # y 좌표에서 경계에 부딪혔을 경우
        if y <= -350 or y >= 350:
            heading = -heading  # 입사각과 반사각: y축 경계를 기준으로 반사

        self.runner.setheading(heading)  # 새로운 반사된 각도로 설정

class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
        self.default_speed = step_move  # 기본 속도 저장
        self.shift_speed = step_move * 2  # 쉬프트 누르면 두 배 속도

        # Register event handlers
        canvas.onkeypress(lambda: self.forward(self.step_move), 'Up')
        canvas.onkeypress(lambda: self.backward(self.step_move), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')

        # Shift 키를 눌렀을 때 속도 증가 및 색상 변경
        canvas.onkeypress(self.increase_speed, 'Shift_L')  # 왼쪽 Shift 키에 반응
        canvas.onkeyrelease(self.reset_speed, 'Shift_L')   # Shift 키를 뗐을 때 속도 복구
        canvas.listen()

    def increase_speed(self):
        """Shift 키를 눌렀을 때 chaser의 속도를 두 배로 증가하고 색상을 빨간색으로 변경 및 메시지 표시"""
        self.step_move = self.shift_speed  # 속도를 두 배로 증가
        self.color('red')  # 색상을 빨간색으로 변경
        self.show_speed_message()  # 메시지 표시

    def reset_speed(self):
        """Shift 키를 놓았을 때 chaser의 속도를 원래대로 복구하고 색상을 초록색으로 변경 및 메시지 제거"""
        self.step_move = self.default_speed  # 속도를 원래 속도로 복구
        self.color('green')  # 색상을 초록색으로 변경
        self.clear_speed_message()  # 메시지 제거

    def show_speed_message(self):
        """왼쪽 상단에 'Turtle Speed Up!' 메시지를 표시"""
        self.canvas = self.getscreen().getcanvas()
        self.canvas.create_text(280, -335, text="Turtle Speed Up!", font=("Arial", 16, "bold"), tags="speed_message")

    def clear_speed_message(self):
        """왼쪽 상단에 표시된 'Turtle Speed Up!' 메시지를 제거"""
        self.canvas = self.getscreen().getcanvas()
        self.canvas.delete("speed_message")

    def run_ai(self, opp_pos, opp_heading):
        pass

class RandomMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn

    def run_ai(self, opp_pos, opp_heading):
        mode = random.randint(0, 2)
        if mode == 0:
            self.forward(self.step_move)
        elif mode == 1:
            self.left(self.step_turn)
        elif mode == 2:
            self.right(self.step_turn)

if __name__ == '__main__':
    # Use 'TurtleScreen' instead of 'Screen' to prevent an exception from the singleton 'Screen'
    root = tk.Tk()
    canvas = tk.Canvas(root, width=700, height=700)
    canvas.pack()
    screen = turtle.TurtleScreen(canvas)

    runner = RandomMover(screen)
    chaser = ManualMover(screen)

    game = RunawayGame(screen, runner, chaser)
    game.start()
    screen.mainloop()
