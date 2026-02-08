import pyxel
import math

# ==========================================
# ★お友達（深海魚）クラス
# ==========================================
class Friend:
    def __init__(self, name, x, y, u, v, w, h, anim_u, anim_v, move_type, facing_left=True):
        self.name = name
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.w = w
        self.h = h
        self.anim_u = anim_v
        self.anim_v = anim_v # 修正: anim_uの代入ミス修正
        self.anim_u = anim_u
        self.move_type = move_type 
        
        self.target_x = x
        self.target_y = y
        
        self.default_facing_left = facing_left
        self.is_moving_right = False 
        
        self.life_timer = 0         
        self.unlit_timer = 0        
        self.max_unlit_time = 60  
        self.is_active = True
        self.is_discovered = False 

    def update(self, screen_w, screen_h):
        self.life_timer += 1
        
        if self.move_type == 'float_low': 
            self.y += pyxel.sin(self.life_timer * 0.1) * 0.2
            
        elif self.move_type == 'float_mid': 
            self.x += pyxel.cos(self.life_timer * 0.05) * 0.1
            self.y += pyxel.sin(self.life_timer * 0.08) * 0.4
            
        elif self.move_type == 'pass': 
            speed = 0.5
            if self.is_moving_right:
                self.x += speed
                if self.x > screen_w: self.is_active = False
            else:
                self.x -= speed
                if self.x < -self.w: self.is_active = False
                
        elif self.move_type == 'swim': 
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            self.x += dx * 0.02
            self.y += dy * 0.02
            if abs(dx) < 5 and abs(dy) < 5:
                self.target_x = pyxel.rndi(10, screen_w - 20)
                if self.name == "FusaAnkou":
                      self.target_y = pyxel.rndi(screen_h - 20, screen_h - 5)
                else:
                      self.target_y = pyxel.rndi(20, screen_h - 20)
            self.is_moving_right = (self.target_x > self.x)

        elif self.move_type == 'static': 
            self.x += pyxel.cos(self.life_timer * 0.05) * 0.1
            self.y += pyxel.sin(self.life_timer * 0.05) * 0.1

    def check_light(self, light_x, light_y, light_r):
        head_x = self.x
        head_y = self.y + self.h / 2
        
        if self.move_type == 'pass' and self.w > 32: 
            if self.is_moving_right:
                head_x = self.x + self.w - 10
            else:
                head_x = self.x + 10
        else:
            head_x = self.x + self.w / 2
            
        dx = head_x - light_x
        dy = head_y - light_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < light_r:
            self.unlit_timer = 0 
            if not self.is_discovered:
                self.is_discovered = True
                return True 
        else:
            self.unlit_timer += 1
            if self.unlit_timer > self.max_unlit_time:
                self.is_active = False 
                
        return False

    def draw(self):
        draw_u = self.u
        draw_v = self.v
        if self.anim_u != -1:
            if (pyxel.frame_count // 15) % 2 == 1:
                draw_u = self.anim_u
                draw_v = self.anim_v
        
        draw_w = self.w
        if self.default_facing_left:
            if self.is_moving_right:
                draw_w = -self.w
        else:
            if not self.is_moving_right:
                draw_w = -self.w
                
        pyxel.blt(self.x, self.y, 0, draw_u, draw_v, draw_w, self.h, 0)


# ==========================================
# ★メインアプリ
# ==========================================
class App:
    def __init__(self):
        self.SCREEN_W = 160
        self.SCREEN_H = 120
        pyxel.init(self.SCREEN_W, self.SCREEN_H, title="Deep Sea Angler: The Cycle of Life")

        try:
            pyxel.load("my_resource.pyxres")
        except FileNotFoundError:
            print("エラー: 'my_resource.pyxres' がありません。")

        # --- ★ここから音の設定 ---
        pyxel.sound(0).set("c3e3", "t", "6", "f", 20)
        pyxel.sound(1).set("c2", "p", "2", "n", 5)
        pyxel.sound(2).set("c2d2", "s", "4", "v", 8)
        pyxel.sound(3).set("c1c2", "n", "1", "s", 3)
        pyxel.sound(4).set("c1r c1", "s", "5", "n", 8)
        pyxel.sound(5).set("c3e3g3c4", "t", "4", "n", 8)
        
        pyxel.sound(6).set(
            "f3 r e3 d3 e3 r f3 r d3 r r r "
            "e3 r c3 a#2 c3 r d3 r a#2 r r r", 
            "s", "4", "n", 45
        )
        pyxel.sound(7).set(
            "f2 r r r r r a#2 r r r r r "
            "g2 r r r r r c2 r r r r r", 
            "s", "5", "f", 45
        )
        
        pyxel.music(0).set([6], [7], [], [])
        # --- ★音の設定終わり ---

        # --- 主人公設定 ---
        self.FISH_W = 16
        self.FISH_H = 16
        self.fish_x = self.SCREEN_W / 2
        self.fish_y = self.SCREEN_H / 2
        self.target_x = self.fish_x
        self.target_y = self.fish_y
        self.is_facing_right = True
        
        # オス設定
        self.male_x = pyxel.rndi(10, 150)
        self.male_y = 130 
        self.male_w = 16; self.male_h = 16
        self.is_male_facing_right = True
        
        # --- ゲームサイクル・スコア関連 ---
        self.phase = 0 
        self.phase_timer = 0
        self.absorbed_count_current_cycle = 0 
        self.total_absorbed_males = 0          
        self.spawn_times = 0                  
        self.survival_frames = 0              
        
        self.TIME_FUSED = 150
        self.TIME_ABSORBING = 150
        
        # 隠しパラメータ: 発情値
        self.estrous = 0
        self.ESTROUS_MAX = 100
        
        # 水温調整
        self.temp_val = 0
        self.temp_target_min = 70
        self.temp_target_max = 90
        self.temp_max = 110
        
        # 演出
        self.egg_ribbon = []
        self.fry_particles = []
        
        # ステータス
        self.hunger = 80
        self.mood = 80
        self.is_alive = True
        self.timer = 0
        self.happy_timer = 0
        self.foods = []
        
        self.bubbles = [[pyxel.rndi(0, self.SCREEN_W), pyxel.rndi(0, self.SCREEN_H), pyxel.rndf(0.5, 1.5), pyxel.rndi(1, 2)] for _ in range(10)]
        self.weeds = [pyxel.rndi(0, self.SCREEN_W) for _ in range(10)]
        self.rocks = [[pyxel.rndi(0, self.SCREEN_W), 120, pyxel.rndi(10, 25), pyxel.rndi(3, 5)] for _ in range(8)]
        
        self.is_dragging = False
        self.is_chasing_food = False

        # コレクション
        self.active_friends = []   
        self.discovered_friends = set() 
        
        self.FRIEND_TYPES = [
            {"name": "Mendako",     "w":16, "h":16, "u":0,  "v":144, "au":16, "av":144, "type":"float_low"},
            {"name": "Ryugu",       "w":64, "h":16, "u":0,  "v":160, "au":-1, "av":-1,  "type":"pass"},
            {"name": "Zarabikunin", "w":16, "h":16, "u":0,  "v":176, "au":16, "av":176, "type":"swim"},
            {"name": "OwanKurage",  "w":16, "h":16, "u":32, "v":176, "au":48, "av":176, "type":"float_mid"},
            {"name": "Ginzame",     "w":32, "h":16, "u":0,  "v":192, "au":0,  "av":208, "type":"swim"}, 
            {"name": "Onikinme",    "w":16, "h":16, "u":32, "v":192, "au":48, "av":192, "type":"swim"},
            {"name": "Oumugai",     "w":16, "h":16, "u":32, "v":208, "au":-1, "av":-1,  "type":"static"},
            {"name": "FusaAnkou",   "w":16, "h":16, "u":0,  "v":224, "au":-1, "av":-1,  "type":"static_low"},
        ]

        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    # ------------------------------------------------
    # ★スマホ操作ヘルパー関数（ここが重要！）
    # キーボードのZ/Xと、ゲームパッドのA/B/X/Yボタン、両方をチェックします
    # ------------------------------------------------
    def is_action_btn_pressed(self):
        # ボタンを押した瞬間（btnp）
        return (pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE) or 
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y))

    def is_cancel_btn_pressed(self):
        # キャンセル/コレクションボタンを押した瞬間（btnp）
        return (pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B) or 
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X))
    
    def is_action_btn_held(self):
        # ボタンを押しっぱなし（btn）
        return (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_SPACE) or 
                pyxel.btn(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_Y))
    
    def is_action_btn_released(self):
        # ボタンを離した瞬間（btnr）
        return (pyxel.btnr(pyxel.KEY_Z) or pyxel.btnr(pyxel.KEY_SPACE) or 
                pyxel.btnr(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_Y))

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.is_alive:
            self.timer += 0.1
            self.survival_frames += 1
            
            # --- ステータス減少 ---
            base_decay_interval = 60
            absorption_penalty = self.total_absorbed_males * 3
            age_penalty = self.survival_frames // 600
            current_decay_interval = max(15, base_decay_interval - absorption_penalty - age_penalty)
            
            if pyxel.frame_count % current_decay_interval == 0:
                self.hunger -= 1
                self.mood -= 1
                if self.mood >= 80 and self.phase == 0:
                    self.estrous = min(self.estrous + 2, self.ESTROUS_MAX)
                if self.hunger <= 0 or self.mood <= 0:
                    self.is_alive = False
                    pyxel.playm(0, loop=True)

            # --- スポーン ---
            if pyxel.frame_count % 60 == 0:
                friend_count = len(self.active_friends)
                spawn_chance = 0
                if friend_count == 0: spawn_chance = 5
                elif friend_count == 1: spawn_chance = 0.5
                else: spawn_chance = 0
                if pyxel.rndi(0, 1000) < (spawn_chance * 10):
                    self.spawn_friend()

            # --- お友達更新 ---
            light_x = self.fish_x + self.FISH_W / 2
            light_y = self.fish_y + self.FISH_H / 2
            light_r = 45 
            for friend in self.active_friends[:]:
                friend.update(self.SCREEN_W, self.SCREEN_H)
                is_new_discovery = friend.check_light(light_x, light_y, light_r)
                if is_new_discovery: self.discovered_friends.add(friend.name)
                if not friend.is_active: self.active_friends.remove(friend)

            # --- ゲーム進行（スマホ対応済）---
            if self.phase == 3:
                # ★長押し判定をヘルパー関数に変更
                is_heating = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT) or self.is_action_btn_held()
                is_release = pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) or self.is_action_btn_released()
                
                if is_heating: 
                    self.temp_val += 1.5
                    if pyxel.frame_count % 4 == 0: pyxel.play(3, 3) 
                else:
                    if self.temp_val > 0: self.temp_val -= 0.5
                
                if is_release or self.temp_val >= self.temp_max:
                    if self.temp_target_min <= self.temp_val <= self.temp_target_max:
                        self.phase = 4; self.spawn_times += 1; self.mood = 100; self.create_egg_ribbon()
                        pyxel.play(2, 5)
                    else:
                        self.mood = max(0, self.mood - 20); self.temp_val = 0
                        pyxel.play(2, 4)
                        if self.mood <= 0: 
                             self.is_alive = False
                             pyxel.playm(0, loop=True)
                self.update_background()
                return

            elif self.phase == 4:
                all_off_screen = True
                for egg in self.egg_ribbon:
                    egg[1] -= 0.8
                    if egg[1] > -20: all_off_screen = False
                if all_off_screen: self.reset_cycle()
                self.update_background()
                return

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                if (self.fish_x <= mx <= self.fish_x + self.FISH_W) and (self.fish_y <= my <= self.fish_y + self.FISH_H):
                    self.is_dragging = True
                else:
                    self.foods.append([mx, 0])
                    if self.phase == 0: self.estrous = min(self.estrous + 5, self.ESTROUS_MAX)
                    self.hunger = min(self.hunger + 10, 100)

            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                self.is_dragging = False
                self.target_x = self.fish_x; self.target_y = self.fish_y

            if self.is_dragging:
                self.fish_x = pyxel.mouse_x - self.FISH_W / 2
                self.fish_y = pyxel.mouse_y - self.FISH_H / 2
                if pyxel.frame_count % 30 == 0: self.mood = max(self.mood - 1, 0)
            else:
                self.update_auto_swim()

            # オス関連サイクル
            if self.phase == 0:
                if self.estrous >= self.ESTROUS_MAX:
                    target_mx = self.fish_x + self.FISH_W / 2 - self.male_w / 2
                    target_my = self.fish_y + self.FISH_H / 2 - self.male_h / 2
                    dx = target_mx - self.male_x; dy = target_my - self.male_y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 5:
                        self.male_x += dx * 0.015; self.male_y += dy * 0.015
                    else:
                        self.phase = 1; self.phase_timer = 0; self.mood = 100
                        self.estrous = 0 
                        self.FISH_W = 32; self.FISH_H = 32; self.fish_x -= 8; self.fish_y -= 8
                        pyxel.play(2, 2)
                    self.is_male_facing_right = (dx > 0)
                else:
                    self.male_x = self.SCREEN_W / 2; self.male_y = self.SCREEN_H + 50

            elif self.phase == 1:
                self.phase_timer += 1
                if self.phase_timer > self.TIME_FUSED:
                    self.phase = 2; self.phase_timer = 0
                    self.FISH_W = 16; self.FISH_H = 16; self.fish_x += 8; self.fish_y += 8
            elif self.phase == 2:
                self.phase_timer += 1
                if self.phase_timer > self.TIME_ABSORBING:
                    self.absorbed_count_current_cycle += 1
                    self.total_absorbed_males += 1 
                    if self.absorbed_count_current_cycle >= 5: self.phase = 3; self.temp_val = 0
                    else: self.reset_cycle()

        # ★アクションボタン判定をヘルパー関数に変更
        if self.is_action_btn_pressed() or pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            if self.is_alive: 
                self.mood = min(self.mood + 10, 100)
                if self.phase == 0: self.estrous = min(self.estrous + 2, self.ESTROUS_MAX)
                self.happy_timer = 90
                pyxel.play(2, 0)

        if self.happy_timer > 0: self.happy_timer -= 1

        if not self.is_alive:
            if self.spawn_times > 0:
                if pyxel.frame_count % 5 == 0: self.fry_particles.append([pyxel.rndi(0, self.SCREEN_W), 0])
                for fry in self.fry_particles: fry[1] += 1
            
            # ★リセットボタン（Rキー、Z/Xキー、ゲームパッドA/Bすべて対応）
            if (pyxel.btnp(pyxel.KEY_R) or 
                self.is_action_btn_pressed() or 
                self.is_cancel_btn_pressed()): 
                self.reset_game_full()

        self.update_foods()
        self.update_background()

    def spawn_friend(self):
        f_data = self.FRIEND_TYPES[pyxel.rndi(0, len(self.FRIEND_TYPES) - 1)]
        spawn_x = pyxel.rndi(0, self.SCREEN_W - f_data["w"])
        spawn_y = pyxel.rndi(20, self.SCREEN_H - 20)
        
        if f_data["type"] == "float_low" or f_data["name"] == "FusaAnkou": 
            spawn_y = pyxel.rndi(self.SCREEN_H - 30, self.SCREEN_H - 16)
        elif f_data["type"] == "pass": 
            if pyxel.rndi(0, 1) == 0:
                spawn_x = -f_data["w"]; facing_right = True 
            else:
                spawn_x = self.SCREEN_W; facing_right = False 
        
        friend = Friend(
            f_data["name"], spawn_x, spawn_y,
            f_data["u"], f_data["v"], f_data["w"], f_data["h"],
            f_data["au"], f_data["av"], f_data["type"]
        )
        if f_data["type"] == "pass": friend.is_moving_right = facing_right
        self.active_friends.append(friend)

    def reset_cycle(self):
        self.phase = 0; self.phase_timer = 0
        self.estrous = 0 
        self.male_x = pyxel.rndi(10, 150); self.male_y = 130
        if self.absorbed_count_current_cycle >= 5: self.absorbed_count_current_cycle = 0

    def reset_game_full(self):
        pyxel.stop()
        self.hunger = 80; self.mood = 80; self.is_alive = True
        self.foods = []; self.happy_timer = 0
        self.fish_x = self.SCREEN_W / 2; self.is_dragging = False
        self.phase = 0; self.phase_timer = 0
        self.FISH_W = 16; self.FISH_H = 16
        self.male_x = 10; self.male_y = 100
        self.estrous = 0
        self.absorbed_count_current_cycle = 0
        self.total_absorbed_males = 0
        self.spawn_times = 0
        self.survival_frames = 0
        self.fry_particles = []
        self.active_friends = [] 

    def create_egg_ribbon(self):
        self.egg_ribbon = []
        start_x = self.fish_x if self.is_facing_right else self.fish_x + self.FISH_W
        start_y = self.fish_y + self.FISH_H // 2
        for i in range(25): self.egg_ribbon.append([start_x, start_y + i * 4])

    def update_background(self):
        for b in self.bubbles:
            b[1] -= b[2]
            if b[1] < -5: b[0], b[1] = pyxel.rndi(0, self.SCREEN_W), self.SCREEN_H + pyxel.rndi(0, 20)

    def update_auto_swim(self):
        self.is_chasing_food = False
        if len(self.foods) > 0:
            nearest_food = None; min_dist = 9999
            for food in self.foods:
                dx = food[0] - self.fish_x; dy = food[1] - self.fish_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < min_dist: min_dist = dist; nearest_food = food
            if nearest_food:
                self.target_x = nearest_food[0] - self.FISH_W / 2
                self.target_y = nearest_food[1] - self.FISH_H / 2
                self.is_chasing_food = True
        else:
            dist_x = self.target_x - self.fish_x; dist_y = self.target_y - self.fish_y
            if abs(dist_x) < 5 and abs(dist_y) < 5:
                self.target_x = pyxel.rndi(10, self.SCREEN_W - self.FISH_W)
                self.target_y = pyxel.rndi(20, self.SCREEN_H - self.FISH_H)
        speed = 0.04 if self.is_chasing_food else 0.02
        self.fish_x += (self.target_x - self.fish_x) * speed
        self.fish_y += (self.target_y - self.fish_y) * speed
        if self.target_x > self.fish_x: self.is_facing_right = True
        elif self.target_x < self.fish_x: self.is_facing_right = False

    def update_foods(self):
        new_foods = []
        for food in self.foods:
            food[1] += 0.5 
            eat_size = 15 if self.phase == 1 else 10
            dx = (food[0]) - (self.fish_x + self.FISH_W/2)
            dy = (food[1]) - (self.fish_y + self.FISH_H/2)
            if not self.is_dragging and abs(dx) < eat_size and abs(dy) < eat_size and self.is_alive: 
                pyxel.play(2, 1)
                pass 
            elif food[1] < self.SCREEN_H: new_foods.append(food)      
        self.foods = new_foods

    def draw(self):
        pyxel.cls(0)

        for b in self.bubbles:
            col = 6 if b[3] == 1 else 7
            pyxel.circ(b[0], b[1], b[3], col)

        for rock in self.rocks:
            pyxel.circ(rock[0], rock[1], rock[2], 0)
            pyxel.circb(rock[0], rock[1], rock[2], 1)
        for i, wx in enumerate(self.weeds):
            sway = pyxel.sin(self.timer * 2 + i) * 10
            pyxel.line(wx, 120, wx + sway, 90 + (i%3)*5, 1)

        if self.is_alive:
            if self.phase == 4:
                for i, egg in enumerate(self.egg_ribbon):
                    wave_x = pyxel.sin(egg[1] * 0.08 + pyxel.frame_count * 0.1) * 6
                    col = 13 if i % 2 == 0 else 6 
                    pyxel.rect(egg[0] + wave_x, egg[1], 3, 3, col)

            for friend in self.active_friends:
                friend.draw()

            if self.phase == 0 and self.estrous >= self.ESTROUS_MAX:
                male_u = 0; male_v = 32
                if (pyxel.frame_count // 10) % 2 == 1: male_u = 32
                male_w = self.male_w if self.is_male_facing_right else -self.male_w
                pyxel.blt(self.male_x, self.male_y, 0, male_u, male_v, male_w, self.male_h, 0)

            draw_x, draw_y = self.fish_x, self.fish_y
            if self.phase == 3: pass
            elif self.happy_timer > 0 and not self.is_dragging:
                draw_x += pyxel.cos(self.timer * 15) * 10; draw_y += pyxel.sin(self.timer * 15) * 10
                pyxel.text(draw_x + self.FISH_W//2 - 4, draw_y - 10, "LOVE", 8)
            elif not self.is_dragging:
                draw_y += pyxel.sin(self.timer * 5) * 3

            if self.phase == 4: pyxel.text(draw_x - 10, draw_y - 15, "Spawning...", 10)

            img_u = 0; img_v = 0
            if self.phase == 1:
                if self.is_dragging: img_u=32; img_v=80; pyxel.text(draw_x+16, draw_y-8, "!", 8)
                elif self.is_chasing_food: img_u=0; img_v=80
                else: img_v=48; 
                if (pyxel.frame_count//15)%2==1 and not self.is_chasing_food: img_u=32
            elif self.phase == 2 or self.phase == 3 or self.phase == 4:
                img_u=16; img_v=112
                if self.is_dragging: img_u=48; img_v=128
                elif self.is_chasing_food and self.phase==2:
                      if(pyxel.frame_count//5)%2==1: img_u=16; img_v=128
                else:
                      if(pyxel.frame_count//15)%2==1: img_u=48; img_v=112
            else:
                if self.is_dragging: img_u=32; img_v=16; pyxel.text(draw_x+8, draw_y-8, "!", 8)
                elif self.is_chasing_food:
                      if(pyxel.frame_count//5)%2==1: img_v=16
                else:
                      if(pyxel.frame_count//15)%2==1: img_u=32

            draw_w = self.FISH_W if self.is_facing_right else -self.FISH_W
            pyxel.blt(draw_x, draw_y, 0, img_u, img_v, draw_w, self.FISH_H, 0)

            sight_r = 45 
            fx = self.fish_x + self.FISH_W / 2
            fy = self.fish_y + self.FISH_H / 2
            black = 0
            pyxel.rect(0, 0, self.SCREEN_W, fy - sight_r, black)
            pyxel.rect(0, fy + sight_r, self.SCREEN_W, self.SCREEN_H - (fy + sight_r), black)
            pyxel.rect(0, fy - sight_r, fx - sight_r, sight_r * 2, black)
            pyxel.rect(fx + sight_r, fy - sight_r, self.SCREEN_W - (fx + sight_r), sight_r * 2, black)
            pyxel.circb(fx, fy, sight_r + 1, 1)
            pyxel.circb(fx, fy, sight_r, 1)
            pyxel.circb(fx, fy, sight_r - 1, 6)

            if self.phase == 3:
                gauge_x = self.SCREEN_W - 15; gauge_y = 20; gauge_h = 80; gauge_w = 6
                pyxel.rectb(gauge_x, gauge_y, gauge_w, gauge_h, 7)
                target_top = gauge_y + gauge_h - (self.temp_target_max / self.temp_max * gauge_h)
                target_height = (self.temp_target_max - self.temp_target_min) / self.temp_max * gauge_h
                pyxel.rect(gauge_x + 1, target_top, gauge_w - 2, target_height, 11)
                current_height = (self.temp_val / self.temp_max) * gauge_h
                pyxel.rect(gauge_x + 1, gauge_y + gauge_h - current_height, gauge_w - 2, current_height, 8)
                pyxel.text(self.SCREEN_W - 60, 10, "HOLD BTN!", 7 if pyxel.frame_count % 10 < 5 else 8)

            pyxel.text(5, 5, f"HUNGER: {self.hunger}", 7)
            pyxel.text(5, 15, f"MOOD:   {self.mood}", 7)
            pyxel.text(5, 25, f"MALES:  {self.absorbed_count_current_cycle}/5", 6)
            
        else:
            # ゲームオーバー
            draw_v = 0
            if self.phase == 1: draw_v = 48
            elif self.phase >= 2: draw_v = 112
            pyxel.blt(self.fish_x, self.fish_y - 10, 0, 0, draw_v, self.FISH_W, -self.FISH_H, 0)
            pyxel.text(self.SCREEN_W//2 - 20, self.SCREEN_H//2 - 20, "GAME OVER", 8)
            
            if self.spawn_times > 0:
                for fry in self.fry_particles:
                    pyxel.pset(fry[0], fry[1], pyxel.rndi(9, 10))
                pyxel.text(self.SCREEN_W//2 - 35, self.SCREEN_H//2 + 5, "LIFE GOES ON...", 10)
                
                offspring_score = (self.spawn_times * 1000) + \
                                  (self.total_absorbed_males * 100) + \
                                  (self.survival_frames // 3)
                pyxel.text(self.SCREEN_W//2 - 30, self.SCREEN_H//2 + 15, f"OFFSPRING: {offspring_score}", 7)
            else:
                pyxel.text(self.SCREEN_W//2 - 30, self.SCREEN_H//2 + 15, "OFFSPRING: 0", 13)

            # リザルト
            pyxel.text(self.SCREEN_W//2 - 40, self.SCREEN_H//2 + 35, "Hold 'B' Btn for Coll.", 7)
            
            # ★キャンセルボタン判定（キーボードX、ゲームパッドB/X）
            if self.is_cancel_btn_pressed():
                pyxel.rect(10, 10, self.SCREEN_W - 20, self.SCREEN_H - 20, 1)
                pyxel.text(60, 15, "COLLECTION", 7)
                
                y_offset = 30
                all_friends = ["Mendako", "Ryugu", "Zarabikunin", "OwanKurage", "Ginzame", "Onikinme", "Oumugai", "FusaAnkou"]
                
                for i, name in enumerate(all_friends):
                    col = 10 if name in self.discovered_friends else 13
                    display_name = name if name in self.discovered_friends else "?????????"
                    col_x = 20 if i < 4 else 90
                    row_y = y_offset + (i % 4) * 15
                    pyxel.text(col_x, row_y, display_name, col)

        for food in self.foods:
            pyxel.rect(food[0], food[1], 3, 3, 10)

App()