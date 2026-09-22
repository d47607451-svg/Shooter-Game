# Create your own shooter

import random
import os
import sys
from pygame import *
		

# --- Settings ---
WIDTH, HEIGHT = 700, 500
CAPTION = "Shooter - Vesmírna bitka"
FPS = 60


def resource_path(relative_path):
	"""Return a path that works both from source and from PyInstaller bundle."""
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def safe_quit():
	"""Safely shut down pygame subsystems without crashing on exit."""
	if display.get_init():
		display.quit()
	if mixer.get_init():
		mixer.quit()
	quit()


class GameSprite(sprite.Sprite):
	def __init__(self, image_path, x, y, speed=0, scale=None):
		super().__init__()
		if os.path.isfile(image_path):
			self.image = image.load(image_path)
			# if a scale tuple is provided, force scale. If scale is None, keep original
			# but ensure the image fits the window (avoid extremely large sprites)
			if scale:
				self.image = transform.scale(self.image, scale)
			else:
				w, h = self.image.get_size()
				max_w, max_h = WIDTH - 20, HEIGHT - 20
				if w > max_w or h > max_h:
					factor = min(max_w / w, max_h / h)
					new_size = (max(1, int(w * factor)), max(1, int(h * factor)))
					self.image = transform.scale(self.image, new_size)
		else:
			# fallback - simple surface
			w, h = scale if scale else (50, 50)
			self.image = Surface((w, h))
			self.image.fill((255, 0, 255))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.speed = speed

	def reset(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
	def __init__(self, image_path, x, y, speed=5, scale=(80, 60)):
		# if an image exists, use GameSprite to load it
		if os.path.isfile(image_path):
			super().__init__(image_path, x, y, speed, scale)
		else:
			# create a rocket-like surface to replace the purple square
			w, h = scale
			surf = Surface((w, h), SRCALPHA)
			# body
			draw.ellipse(surf, (180, 180, 180), (w * 0.25, 0, w * 0.5, h * 0.9))
			# nose
			draw.polygon(surf, (80, 80, 80), [(w * 0.25, 0), (w * 0.5, -h * 0.15), (w * 0.75, 0)])
			# left/right fins
			draw.polygon(surf, (120, 120, 120), [(0, h * 0.55), (w * 0.25, h * 0.5), (w * 0.25, h * 0.75)])
			draw.polygon(surf, (120, 120, 120), [(w, h * 0.55), (w * 0.75, h * 0.5), (w * 0.75, h * 0.75)])
			# windows
			for i, py in enumerate([h * 0.25, h * 0.45, h * 0.65]):
				draw.circle(surf, (255, 215, 0), (int(w * 0.5), int(py)), int(h * 0.08))
				draw.circle(surf, (0, 0, 0), (int(w * 0.5), int(py)), int(h * 0.08), 2)

			self.image = surf
			self.rect = self.image.get_rect()
			self.rect.x = x
			self.rect.y = y
			self.speed = speed

	def update(self):
		keys = key.get_pressed()
		if keys[K_a] and self.rect.x > 0:
			self.rect.x -= self.speed
		if keys[K_d] and self.rect.x + self.rect.width < WIDTH:
			self.rect.x += self.speed


class Enemy(GameSprite):
	def __init__(self, image_path, x, y, speed=3, scale=(60, 40)):
		super().__init__(image_path, x, y, speed, scale)

	def update(self):
		self.rect.y += self.speed
		# movement only; don't auto-respawn here so main loop can count misses


class Bullet(sprite.Sprite):
	def __init__(self, x, y, speed=7):
		super().__init__()
		self.image = Surface((4, 10))
		self.image.fill((255, 255, 0))
		self.rect = self.image.get_rect(center=(x, y))
		self.speed = speed

	def update(self):
		self.rect.y -= self.speed
		if self.rect.y < -10:
			self.kill()


def main():
	init()
	mixer.init()
	try:
		screen = display.set_mode((WIDTH, HEIGHT))
		display.set_caption(CAPTION)
		clock = time.Clock()

		# background image if exists
		bg = None
		bg_path = resource_path('galaxy.jpg')
		if os.path.isfile(bg_path):
			bg = image.load(bg_path)
			bg = transform.scale(bg, (WIDTH, HEIGHT))

		# background music
		space_path = resource_path('space.ogg')
		if os.path.isfile(space_path):
			try:
				mixer.music.load(space_path)
				mixer.music.play(-1)
			except Exception:
				pass

		# fire sound (played when shooting)
		fire_sound = None
		fire_path = resource_path('fire.ogg')
		if os.path.isfile(fire_path):
			try:
				fire_sound = mixer.Sound(fire_path)
			except Exception:
				fire_sound = None

		# player (use rocket.png if available)
		player = Player(resource_path('rocket.png'), WIDTH // 2 - 40, HEIGHT - 80, speed=6)

		# enemies group
		enemies = sprite.Group()
		for i in range(5):
			x = random.randint(0, WIDTH - 60)
			y = random.randint(-400, -40)
			e = Enemy(resource_path('ufo.png'), x, y, speed=random.randint(2, 5))
			enemies.add(e)

		bullets = sprite.Group()

		# fonts and counters
		font.init()
		game_font = font.SysFont('Arial', 24)
		hits = 0
		missed = 0

		# shooting cooldown (ms)
		shot_cooldown = 100
		last_shot = 0

		running = True
		end_message = None
		end_color = (255, 0, 0)
		while running:
			for ev in event.get():
				if ev.type == QUIT:
					running = False
				elif ev.type == KEYDOWN:
					if ev.key == K_SPACE:
						# allow firing only if cooldown elapsed
						now = time.get_ticks()
						if now - last_shot >= shot_cooldown:
							# fire bullet from top-center of player
							bx = player.rect.centerx
							by = player.rect.top
							bullets.add(Bullet(bx, by))
							last_shot = now
							if fire_sound:
								try:
									fire_sound.play()
								except Exception:
									pass
				elif ev.type == MOUSEBUTTONDOWN:
					# left mouse button (1) fires a bullet
					if ev.button == 1:
						now = time.get_ticks()
						if now - last_shot >= shot_cooldown:
							bx = player.rect.centerx
							by = player.rect.top
							bullets.add(Bullet(bx, by))
							last_shot = now
							if fire_sound:
								try:
									fire_sound.play()
								except Exception:
									pass

			# updates
			player.update()
			enemies.update()
			bullets.update()

			# check enemies that moved past bottom -> count missed and respawn
			for e in enemies:
				if e.rect.y > HEIGHT:
					missed += 1
					e.rect.y = -random.randint(40, 200)
					e.rect.x = random.randint(0, WIDTH - e.rect.width)

			# collisions bullets <-> enemies
			collisions = sprite.groupcollide(enemies, bullets, False, True)
			if collisions:
				for enemy_obj in collisions.keys():
					hits += 1
					# respawn enemy at top
					enemy_obj.rect.y = -random.randint(40, 200)
					enemy_obj.rect.x = random.randint(0, WIDTH - enemy_obj.rect.width)

			# check collision between player and any enemy -> lose
			if sprite.spritecollideany(player, enemies):
				end_message = "Prehra: Zrazka s nepriatelom"
				end_color = (200, 30, 30)
				running = False

			# win/loss conditions based on counters
			if hits >= 10:
				end_message = "Vyhral si!"
				end_color = (50, 200, 50)
				running = False

			if missed >= 5:
				end_message = "Prehra: Prilis mnoho netrafenych"
				end_color = (200, 30, 30)
				running = False

			# draw
			if bg:
				screen.blit(bg, (0, 0))
			else:
				screen.fill((10, 10, 30))

			# draw sprites
			player.reset(screen)
			enemies.draw(screen)
			bullets.draw(screen)

			# HUD
			txt_hits = game_font.render(f"Zasiahnuté: {hits}", True, (255, 255, 255))
			txt_missed = game_font.render(f"Netrafené: {missed}", True, (255, 255, 255))
			screen.blit(txt_hits, (10, 10))
			screen.blit(txt_missed, (10, 40))

			display.flip()
			clock.tick(FPS)

		# if the game ended due to win/lose, show message for a short time
		if end_message:
			# render a larger message
			big_font = font.SysFont('Arial', 48)
			msg = big_font.render(end_message, True, end_color)
			msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
			screen.blit(msg, msg_rect)
			display.flip()
			# wait 2.5 seconds or until user closes
			end_wait = time.get_ticks() + 2500
			while time.get_ticks() < end_wait:
				for ev in event.get():
					if ev.type == QUIT:
						running = False
				# small delay to avoid busy loop
				time.delay(50)
	finally:
		safe_quit()


if __name__ == '__main__':
	main()
