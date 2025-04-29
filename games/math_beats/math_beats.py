import pygame
import random
import os
import json
import math

class MathBeats:
    def __init__(self, difficulty="medium"):
        pygame.init()
        pygame.mixer.init()  # Initialize the mixer for sound
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Math Beats")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game settings
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.score = 0
        self.player_name = "Player"
        self.game_over = False
        self.time_left = 60  # 60 seconds game time
        self.last_time_check = pygame.time.get_ticks()
        
        # Math problem settings
        self.current_problem = None
        self.current_answer = None
        self.player_answer = ""
        self.answer_correct = None
        self.problems_solved = 0
        self.combo = 0
        
        # Beat settings
        self.beat_interval = 1000  # milliseconds between beats
        self.last_beat_time = pygame.time.get_ticks()
        self.beat_active = False
        self.beat_duration = 300  # milliseconds each beat is active
        self.beat_radius = 50
        self.beat_max_radius = 100
        self.beat_color = (0, 255, 0)
        
        # Set up fonts
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)
        self.tiny_font = pygame.font.SysFont(None, 24)
        
        # Set difficulty parameters
        self.set_difficulty(difficulty)
        
        # Generate first problem
        self.generate_problem()

    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            self.operations = ['+', '-']
            self.number_range = (1, 10)
            self.beat_interval = 1200  # Slower rhythm
        elif difficulty == "medium":
            self.operations = ['+', '-', '*']
            self.number_range = (1, 20)
            self.beat_interval = 1000
        elif difficulty == "hard":
            self.operations = ['+', '-', '*', '/']
            self.number_range = (1, 50)
            self.beat_interval = 800  # Faster rhythm
            
    def generate_problem(self):
        operation = random.choice(self.operations)
        
        if operation == '+':
            num1 = random.randint(*self.number_range)
            num2 = random.randint(*self.number_range)
            answer = num1 + num2
            problem = f"{num1} + {num2}"
        elif operation == '-':
            num1 = random.randint(*self.number_range)
            num2 = random.randint(*self.number_range)
            # Make sure num1 >= num2 to avoid negative answers for simplicity
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
            problem = f"{num1} - {num2}"
        elif operation == '*':
            # Smaller range for multiplication
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            answer = num1 * num2
            problem = f"{num1} × {num2}"
        elif operation == '/':
            # Make sure division results in a whole number
            num2 = random.randint(1, 10)  # divisor
            num1 = num2 * random.randint(1, 10)  # to ensure whole number result
            answer = num1 // num2
            problem = f"{num1} ÷ {num2}"
            
        self.current_problem = problem
        self.current_answer = str(answer)
        self.player_answer = ""

    def run(self):
        # Show start menu before the game
        self.show_start_menu()
        
        # Main game loop
        while self.running:
            self.handle_events()
            
            if not self.game_over:
                self.update()
            
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        
    def show_start_menu(self):
        menu_running = True
        difficulty_options = ["easy", "medium", "hard"]
        selected_difficulty = 1  # Default to medium
        
        # Input box for player name
        name_input = ""
        name_input_active = True
        
        while menu_running:
            self.screen.fill((0, 0, 0))  # Black background
            
            # Title
            title = self.font.render("Math Beats", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
            
            # Name input box
            name_prompt = self.small_font.render("Enter your name:", True, (255, 255, 255))
            self.screen.blit(name_prompt, (self.width // 2 - name_prompt.get_width() // 2, 200))
            
            # Draw input box
            input_box = pygame.Rect(self.width // 2 - 100, 250, 200, 40)
            color = (100, 100, 200) if name_input_active else (70, 70, 70)
            pygame.draw.rect(self.screen, color, input_box, 2)
            
            # Render current name input
            name_surface = self.small_font.render(name_input, True, (255, 255, 255))
            self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
            
            # Difficulty selection
            diff_text = self.small_font.render("Select Difficulty:", True, (255, 255, 255))
            self.screen.blit(diff_text, (self.width // 2 - diff_text.get_width() // 2, 330))
            
            for i, diff in enumerate(difficulty_options):
                color = (0, 255, 0) if i == selected_difficulty else (255, 255, 255)
                diff_option = self.small_font.render(diff.title(), True, color)
                self.screen.blit(diff_option, (self.width // 2 - diff_option.get_width() // 2, 380 + i * 40))
            
            # Start button
            start_text = self.small_font.render("Start Game", True, (0, 0, 0))
            start_rect = start_text.get_rect(center=(self.width // 2, 520))
            pygame.draw.rect(self.screen, (0, 255, 0), (start_rect.x - 10, start_rect.y - 10, 
                                                      start_rect.width + 20, start_rect.height + 20))
            self.screen.blit(start_text, start_rect)
            
            # Game instructions
            instructions = [
                "Solve math problems to the rhythm of the beat!",
                "Type your answer and press Enter when the circle is green.",
                "Correct answers on the beat give bonus points!"
            ]
            
            for i, instruction in enumerate(instructions):
                instr_text = self.tiny_font.render(instruction, True, (255, 255, 255))
                self.screen.blit(instr_text, (self.width // 2 - instr_text.get_width() // 2, 570 + i * 25))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    self.running = False
                    return
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if input box was clicked
                    if input_box.collidepoint(event.pos):
                        name_input_active = True
                    else:
                        name_input_active = False
                        
                    # Check if difficulty options were clicked
                    for i, _ in enumerate(difficulty_options):
                        option_rect = pygame.Rect(self.width // 2 - 50, 380 + i * 40, 100, 30)
                        if option_rect.collidepoint(event.pos):
                            selected_difficulty = i
                            
                    # Check if start button was clicked
                    if start_rect.collidepoint(event.pos) and name_input:
                        self.player_name = name_input
                        self.difficulty = difficulty_options[selected_difficulty]
                        self.set_difficulty(self.difficulty)
                        self.time_left = 60  # Reset timer
                        self.score = 0       # Reset score
                        self.last_time_check = pygame.time.get_ticks()
                        menu_running = False
                        
                elif event.type == pygame.KEYDOWN:
                    if name_input_active:
                        if event.key == pygame.K_RETURN:
                            if name_input:
                                name_input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            name_input = name_input[:-1]
                        else:
                            # Limit name length to 10 characters
                            if len(name_input) < 10:
                                name_input += event.unicode
                                
                    # Navigate difficulty with arrow keys
                    if event.key == pygame.K_UP:
                        selected_difficulty = max(0, selected_difficulty - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_difficulty = min(len(difficulty_options) - 1, selected_difficulty + 1)
                    elif event.key == pygame.K_RETURN:
                        if name_input:
                            self.player_name = name_input
                            self.difficulty = difficulty_options[selected_difficulty]
                            self.set_difficulty(self.difficulty)
                            self.time_left = 60  # Reset timer
                            self.score = 0       # Reset score
                            self.last_time_check = pygame.time.get_ticks()
                            menu_running = False
                        
            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                else:
                    if event.key == pygame.K_RETURN:
                        self.check_answer()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_answer = self.player_answer[:-1]
                    elif event.unicode.isdigit() or event.unicode == '-':
                        # Only allow digits and minus sign
                        self.player_answer += event.unicode

    def check_answer(self):
        # Check if player's answer is correct
        if self.player_answer == self.current_answer:
            # Calculate score based on timing with the beat
            current_time = pygame.time.get_ticks()
            time_since_beat = (current_time - self.last_beat_time) % self.beat_interval
            
            # Check if answer was submitted during the beat window
            if self.beat_active:
                self.score += 20  # Bonus for answering on beat
                self.combo += 1
                self.answer_correct = True
            else:
                self.score += 10
                self.combo = 0
                self.answer_correct = True
                
            # Apply combo bonus
            if self.combo > 1:
                combo_bonus = 5 * self.combo
                self.score += combo_bonus
        else:
            self.combo = 0
            self.answer_correct = False
            
        # Generate new problem
        self.problems_solved += 1
        self.generate_problem()

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update timer
        if current_time - self.last_time_check >= 1000:  # 1 second has passed
            self.time_left -= 1
            self.last_time_check = current_time
            
            if self.time_left <= 0:
                self.game_over = True
                self.save_score()
        
        # Update beat
        time_since_beat = (current_time - self.last_beat_time) % self.beat_interval
        
        if time_since_beat < self.beat_duration:
            self.beat_active = True
            # Calculate beat radius based on time since beat started
            progress = time_since_beat / self.beat_duration
            self.beat_radius = int(self.beat_max_radius * (1 - progress))
            self.beat_color = (0, 255, 0)  # Green when active
        else:
            self.beat_active = False
            self.beat_color = (150, 150, 150)  # Gray when inactive
            self.beat_radius = self.beat_max_radius // 2
            
        # Update beat timer
        if current_time - self.last_beat_time >= self.beat_interval:
            self.last_beat_time = current_time - (current_time - self.last_beat_time) % self.beat_interval
            # Play beat sound effect here if you have one

    def draw(self):
        # Draw dark music-themed background
        self.screen.fill((20, 20, 40))  # Dark blue/purple
        
        # Draw musical note patterns
        for i in range(20):
            x = (i * 50) % self.width
            y = ((i * 70) % self.height) + math.sin(pygame.time.get_ticks() / 1000 + i) * 20
            color = ((i * 10) % 200 + 55, 100, 200)
            size = (i % 3 + 1) * 5
            pygame.draw.circle(self.screen, color, (int(x), int(y)), size)
        
        # Draw beat circle
        pygame.draw.circle(self.screen, self.beat_color, (self.width // 2, self.height // 2 - 100), self.beat_radius, 5)
        
        # Draw current problem
        problem_text = self.font.render(self.current_problem + " = ?", True, (255, 255, 255))
        self.screen.blit(problem_text, (self.width // 2 - problem_text.get_width() // 2, self.height // 2 - 150))
        
        # Draw input box
        input_box = pygame.Rect(self.width // 2 - 100, self.height // 2 - 50, 200, 50)
        pygame.draw.rect(self.screen, (50, 50, 70), input_box)
        pygame.draw.rect(self.screen, (200, 200, 200), input_box, 2)
        
        # Draw player's answer
        if self.player_answer:
            answer_text = self.font.render(self.player_answer, True, (255, 255, 255))
            self.screen.blit(answer_text, (input_box.x + 20, input_box.y + 10))
        
        # Draw feedback for previous answer
        if self.answer_correct is not None:
            if self.answer_correct:
                feedback_text = self.small_font.render("Correct!", True, (0, 255, 0))
            else:
                feedback_text = self.small_font.render(f"Wrong! Answer: {self.current_answer}", True, (255, 0, 0))
            self.screen.blit(feedback_text, (self.width // 2 - feedback_text.get_width() // 2, self.height // 2 + 20))
        
        # Draw combo
        if self.combo > 1:
            combo_text = self.small_font.render(f"Combo: x{self.combo}", True, (255, 255, 0))
            self.screen.blit(combo_text, (self.width // 2 - combo_text.get_width() // 2, self.height // 2 + 60))
        
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        
        # Draw time left
        time_text = self.small_font.render(f"Time: {self.time_left}", True, (255, 255, 255))
        self.screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))
        
        # Draw player name and difficulty
        info_text = self.tiny_font.render(f"Player: {self.player_name} | Difficulty: {self.difficulty.title()}", True, (200, 200, 200))
        self.screen.blit(info_text, (20, self.height - 30))
        
        # Draw instruction
        instruction = self.tiny_font.render("Type your answer and press Enter on the beat for bonus points!", True, (200, 200, 200))
        self.screen.blit(instruction, (self.width // 2 - instruction.get_width() // 2, self.height - 60))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 80))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2 - 20))
            
            problems_text = self.small_font.render(f"Problems Solved: {self.problems_solved}", True, (255, 255, 255))
            self.screen.blit(problems_text, (self.width // 2 - problems_text.get_width() // 2, self.height // 2 + 20))
            
            restart_text = self.small_font.render("Press ENTER to play again", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 70))
        
        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.time_left = 60
        self.last_time_check = pygame.time.get_ticks()
        self.problems_solved = 0
        self.combo = 0
        self.answer_correct = None
        self.generate_problem()

    def save_score(self):
        # Create scores directory if it doesn't exist
        if not os.path.exists("scores"):
            os.makedirs("scores")
            
        # Score file path - match the launcher's expected format
        score_file = "scores/math_beats_scores.json"
        
        # Load existing scores
        scores = []
        if os.path.exists(score_file):
            try:
                with open(score_file, 'r') as f:
                    scores = json.load(f)
            except:
                scores = []
                
        # Add current score
        scores.append({
            "name": self.player_name,
            "score": self.score,
            "difficulty": self.difficulty,
            "problems_solved": self.problems_solved
        })
        
        # Save scores
        with open(score_file, 'w') as f:
            json.dump(scores, f)

if __name__ == "__main__":
    game = MathBeats()
    game.run()
