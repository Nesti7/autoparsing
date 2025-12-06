import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Простой 2D Платформер")

# Цвета (R, G, B)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Настройки игры
FPS = 60
clock = pygame.time.Clock()

# Шрифт для отображения счёта
font = pygame.font.Font(None, 36)
score = 0 # Начальное количество собранных монеток

# Класс для игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 60)) # Размер героя
        self.image.fill(BLUE) # Цвет героя
        self.rect = self.image.get_rect()
        self.rect.x = 50 # Начальная позиция X
        self.rect.y = SCREEN_HEIGHT - 50 - 60 # Начальная позиция Y (выше пола)

        self.change_x = 0 # Изменение позиции по X
        self.change_y = 0 # Изменение позиции по Y (для прыжка и гравитации)
        self.on_ground = False # Флаг, указывающий, стоит ли игрок на земле

    def update(self):
        # Гравитация
        self.calc_gravity()

        # Движение по X
        self.rect.x += self.change_x

        # Проверка коллизий по X
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.change_x > 0: # Движение вправо
                self.rect.right = block.rect.left
            elif self.change_x < 0: # Движение влево
                self.rect.left = block.rect.right

        # Движение по Y
        self.rect.y += self.change_y

        # Проверка коллизий по Y
        block_hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for block in block_hit_list:
            if self.change_y > 0: # Падение
                self.rect.bottom = block.rect.top
                self.change_y = 0
                self.on_ground = True # Игрок на земле
            elif self.change_y < 0: # Прыжок
                self.rect.top = block.rect.bottom
                self.change_y = 0
            
            # Убедимся, что игрок не застревает в платформе, если он уже на ней
            # Это может произойти, если он "залип" в платформе после коллизии по X
            if self.rect.bottom > block.rect.top and self.rect.top < block.rect.bottom:
                 if self.change_x == 0: # Только если игрок не двигался по X, предотвращаем застревание
                    if self.change_y == 0 and self.rect.bottom - block.rect.top < 10: # Небольшой допуск
                        self.rect.bottom = block.rect.top
                        self.on_ground = True

        # Проверка, если игрок упал с платформы
        # Убрана часть логики, которая могла приводить к "залипанию" игрока в воздухе
        if self.change_y > 1: # Если игрок падает
            self.on_ground = False

        # Проверка выхода за пределы экрана по X
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def calc_gravity(self):
        # Применяем гравитацию
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 1
        
        # Максимальная скорость падения (чтобы не проваливаться сквозь платформы)
        if self.change_y > 10:
            self.change_y = 10

        # Убираем этот флаг, так как он сбрасывается в update
        # self.on_ground = False # Сбрасываем флаг, будет установлен в update, если есть коллизия по Y

    def jump(self):
        # Прыжок только если игрок на земле
        if self.on_ground:
            self.change_y = -15 # Скорость прыжка
            self.on_ground = False # Игрок больше не на земле

    # Методы для управления движением
    def go_left(self):
        self.change_x = -5

    def go_right(self):
        self.change_x = 5

    def stop(self):
        self.change_x = 0

# Класс для платформ
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN) # Цвет платформы
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс для монеток
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA) # Создаем поверхность с альфа-каналом
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10) # Рисуем круг
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) # Центр монетки

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()

# Создание игрока
player = Player()
all_sprites.add(player)

# Создание платформ
ground = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50) # Пол
platform1 = Platform(200, 400, 200, 20)
platform2 = Platform(500, 300, 150, 20)
platform3 = Platform(100, 200, 100, 20)

platforms.add(ground, platform1, platform2, platform3)
all_sprites.add(ground, platform1, platform2, platform3)

# Создание монеток
coin1 = Coin(250, 350)
coin2 = Coin(550, 250)
coin3 = Coin(150, 150)

coins.add(coin1, coin2, coin3)
all_sprites.add(coin1, coin2, coin3)

# Основной игровой цикл
running = True
game_over = False # Флаг окончания игры
win = False # Флаг победы

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обработка нажатых клавиш (постоянная проверка)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.go_left()
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.go_right()
    else:
        player.stop()

    if keys[pygame.K_SPACE] and not game_over and not win:
        player.jump()

    if not game_over and not win:
        # Обновление спрайтов
        all_sprites.update()

        # Проверка сбора монеток
        collected_coins = pygame.sprite.spritecollide(player, coins, True) # True - удалить монетку при столкновении
        score += len(collected_coins) # Увеличиваем счётчик

        # Проверка проигрыша (падение ниже экрана)
        if player.rect.top > SCREEN_HEIGHT:
            print("Игра окончена: упал!")
            game_over = True

        # Проверка победы (собраны все монетки)
        if score >= 3:
            print("Поздравляем! Вы собрали все монетки!")
            win = True

    # Очистка экрана
    SCREEN.fill(WHITE)

    # Рисование всех спрайтов
    all_sprites.draw(SCREEN)

    # Отображение счёта
    score_text = font.render(f"Монетки: {score}/3", True, BLACK)
    SCREEN.blit(score_text, (10, 10))

    # Обновление экрана
    pygame.display.flip()

    # Ограничение частоты кадров
    clock.tick(FPS)

# Завершение Pygame
pygame.quit()
sys.exit()
