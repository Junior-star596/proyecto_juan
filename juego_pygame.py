import pygame
import random
import math
from enum import Enum
import heapq

# Inicialización de Pygame
pygame.init()

# Constantes
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
GRIS = (128, 128, 128)

# Estados del juego
class EstadoJuego(Enum):
    MENU = 1
    JUGANDO = 2
    NUEVA_RONDA = 3
    JUEGO_TERMINADO = 4
    VICTORIA = 5


# Clase para el botón del menú
class BotonMenu:
    def __init__(self, x, y, ancho, alto, texto, color=AZUL, color_hover=VERDE):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.color_actual = color
        self.fuente = pygame.font.Font(None, 32)
        self.esta_hover = False

    def dibujar(self, pantalla):
        # Dibujar el botón
        pygame.draw.rect(pantalla, self.color_actual, self.rect, 0, 10)
        pygame.draw.rect(pantalla, BLANCO, self.rect, 3, 10)

        # Dibujar el texto
        texto_renderizado = self.fuente.render(self.texto, True, BLANCO)
        rect_texto = texto_renderizado.get_rect(center=self.rect.center)
        pantalla.blit(texto_renderizado, rect_texto)

    def actualizar(self, pos_mouse):
        # Verificar si el mouse está sobre el botón
        if self.rect.collidepoint(pos_mouse):
            self.color_actual = self.color_hover
            self.esta_hover = True
        else:
            self.color_actual = self.color
            self.esta_hover = False

    def es_pulsado(self):
        return self.esta_hover and pygame.mouse.get_pressed()[0]


# Clase para el jugador
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.imagen = pygame.Surface((40, 20))
        self.imagen.fill(VERDE)
        self.image = self.imagen  # Añadido para compatibilidad con Pygame
        self.rect = self.imagen.get_rect()
        self.rect.centerx = ANCHO_PANTALLA // 2
        self.rect.bottom = ALTO_PANTALLA - 100
        self.velocidad = 5
        self.retraso_disparo = 250
        self.ultimo_disparo = pygame.time.get_ticks()

    def update(self):  # Renombrado para compatibilidad con Pygame
        self.actualizar()

    def actualizar(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad

        # Mantener al jugador dentro de la pantalla
        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))

    def disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.retraso_disparo:
            self.ultimo_disparo = ahora
            return Bala(self.rect.centerx, self.rect.top)
        return None

# Clase para las balas
class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.imagen = pygame.Surface((4, 10))
        self.imagen.fill(BLANCO)
        self.image = self.imagen  # Añadido para compatibilidad con Pygame
        self.rect = self.imagen.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.velocidad = -10

    def update(self):  # Renombrado para compatibilidad con Pygame
        self.actualizar()

    def actualizar(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0:
            self.kill()


