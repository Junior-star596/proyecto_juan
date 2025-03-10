import pygame
import random
import math
from enum import Enum
import heapq
import time


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


# Clase para las ciudades
class Ciudad(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.imagen = pygame.Surface((60, 40))
        self.imagen.fill(AZUL)
        self.image = self.imagen  # Añadido para compatibilidad con Pygame
        self.rect = self.imagen.get_rect()
        self.rect.centerx = x
        self.rect.bottom = ALTO_PANTALLA - 20


# Clase para los enemigos
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, ciudades_objetivo):
        super().__init__()
        self.imagen = pygame.Surface((30, 30))
        self.imagen.fill(ROJO)
        self.image = self.imagen  # Añadido para compatibilidad con Pygame
        self.rect = self.imagen.get_rect()
        self.rect.x = random.randint(0, ANCHO_PANTALLA - self.rect.width)
        self.rect.y = -self.rect.height
        self.velocidad = 2
        self.ciudades_objetivo = ciudades_objetivo
        self.objetivo_actual = random.choice(ciudades_objetivo) if ciudades_objetivo else None

    def update(self):  # Renombrado para compatibilidad con Pygame
        self.actualizar()

    def actualizar(self):
        if not self.objetivo_actual:
            self.kill()
            return

        # Comportamiento simple: moverse hacia la ciudad objetivo
        dx = self.objetivo_actual.rect.centerx - self.rect.centerx
        dy = self.objetivo_actual.rect.centery - self.rect.centery

        distancia = math.sqrt(dx ** 2 + dy ** 2)
        if distancia != 0:
            dx = dx / distancia * self.velocidad
            dy = dy / distancia * self.velocidad

        self.rect.x += dx
        self.rect.y += dy

        # Verificar si ha llegado a la parte inferior de la pantalla
        if self.rect.top > ALTO_PANTALLA:
            self.kill()
            return


# Implementación del Árbol de Comportamiento
class Nodo:
    def __init__(self):
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def ejecutar(self):
        pass


class Selector(Nodo):
    def ejecutar(self):
        for hijo in self.hijos:
            if hijo.ejecutar():
                return True
        return False


class Secuencia(Nodo):
    def ejecutar(self):
        for hijo in self.hijos:
            if not hijo.ejecutar():
                return False
        return True


class Accion(Nodo):
    def __init__(self, accion):
        super().__init__()
        self.accion = accion

    def ejecutar(self):
        return self.accion()


class Invertir(Nodo):
    def __init__(self, accion):
        super().__init__()
        self.agregar_hijo(accion)

    def ejecutar(self):
        return not self.hijos[0].ejecutar()


class Timer(Nodo):
    def __init__(self, tiempo):
        super().__init__()
        self.tiempo = tiempo
        self.tiempo_restante = tiempo

    def ejecutar(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            return False
        else:
            self.tiempo_restante = self.tiempo
            for hijo in self.hijos:
                hijo.ejecutar()
            return True


class EnemigoAvanzado(pygame.sprite.Sprite):
    def __init__(self, ciudades_objetivo, jugador, juego=None):
        super().__init__()
        self.imagen = pygame.Surface((30, 30))
        self.imagen.fill(ROJO)
        self.image = self.imagen
        self.rect = self.imagen.get_rect()
        self.rect.x = random.randint(0, ANCHO_PANTALLA - self.rect.width)
        self.rect.y = -self.rect.height
        self.velocidad = 2
        self.ciudades_objetivo = ciudades_objetivo
        self.objetivo_actual = random.choice(ciudades_objetivo) if ciudades_objetivo else None
        self.jugador = jugador
        self.juego = juego
        self.vida = 3
        self.tiempo_cambio_objetivo = 100

        # Configuración del árbol de comportamiento
        self.configurar_arbol()

    def configurar_arbol(self):
        # Nodo principal (Selector)
        self.comportamiento = Selector()

        # Ramas principales
        secuencia_evadir = Secuencia()
        secuencia_atacar_ciudad = Secuencia()

        # Agregar ramas al nodo principal
        self.comportamiento.agregar_hijo(secuencia_evadir)
        self.comportamiento.agregar_hijo(secuencia_atacar_ciudad)

        # Condiciones y acciones para evadir
        en_peligro = Accion(self.esta_en_peligro)
        evadir = Accion(self.evadir_peligro)
        secuencia_evadir.agregar_hijo(en_peligro)
        secuencia_evadir.agregar_hijo(evadir)

        # Condiciones y acciones para atacar ciudad
        hay_objetivo = Accion(lambda: self.objetivo_actual is not None)
        atacar_ciudad = Accion(self.mover_hacia_objetivo)

        timer_cambio = Timer(self.tiempo_cambio_objetivo)
        timer_cambio.agregar_hijo(Accion(self.cambiar_objetivo_aleatorio))

        secuencia_atacar_ciudad.agregar_hijo(hay_objetivo)
        secuencia_atacar_ciudad.agregar_hijo(atacar_ciudad)
        secuencia_atacar_ciudad.agregar_hijo(timer_cambio)

    def esta_en_peligro(self):
        # Detectar si hay disparos cerca
        if not hasattr(self, 'juego') or not self.juego:
            return False

        for bala in self.juego.balas:
            dx = bala.rect.centerx - self.rect.centerx
            dy = bala.rect.centery - self.rect.centery
            distancia = math.sqrt(dx ** 2 + dy ** 2)

            # Si hay una bala a menos de 100 píxeles
            if distancia < 100 and bala.rect.y > self.rect.y:
                return True

        return False

    def evadir_peligro(self):
        # Movimiento evasivo aleatorio
        self.rect.x += random.choice([-1, 1]) * self.velocidad * 2

        # Mantener dentro de los límites de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > ANCHO_PANTALLA:
            self.rect.right = ANCHO_PANTALLA

        return True

    def mover_hacia_objetivo(self):
        if not self.objetivo_actual:
            return False

        dx = self.objetivo_actual.rect.centerx - self.rect.centerx
        dy = self.objetivo_actual.rect.centery - self.rect.centery

        distancia = math.sqrt(dx ** 2 + dy ** 2)
        if distancia != 0:
            dx = dx / distancia * self.velocidad
            dy = dy / distancia * self.velocidad

        self.rect.x += dx
        self.rect.y += dy

        return True

    def cambiar_objetivo_aleatorio(self):
        if self.ciudades_objetivo:
            self.objetivo_actual = random.choice(self.ciudades_objetivo)
        return True

    def recibir_impacto(self):
        self.vida -= 1
        if self.vida <= 0:
            self.kill()
        return True

    def update(self):
        self.actualizar()

    def actualizar(self):
        # Ejecutar el árbol de comportamiento
        self.comportamiento.ejecutar()

        # Verificar si ha llegado a la parte inferior de la pantalla
        if self.rect.top > ALTO_PANTALLA:
            self.kill()
            return


