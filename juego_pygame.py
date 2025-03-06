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

