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


# Clase principal del juego
class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Defensor Espacial")
        self.reloj = pygame.time.Clock()
        self.estado = EstadoJuego.MENU
        self.fuente = pygame.font.Font(None, 64)
        self.fuente_pequena = pygame.font.Font(None, 32)

        # Crear botones para el menú
        centro_x = ANCHO_PANTALLA // 2
        self.boton_jugar = BotonMenu(centro_x - 100, ALTO_PANTALLA // 2, 200, 50, "JUGAR")
        self.boton_salir = BotonMenu(centro_x - 100, ALTO_PANTALLA // 2 + 80, 200, 50, "SALIR", ROJO)

        # Agregar modo de enemigos avanzados
        self.usar_enemigos_avanzados = True
        self.boton_modo = BotonMenu(centro_x - 100, ALTO_PANTALLA // 2 + 160, 200, 50, "MODO: AVANZADO", AMARILLO)

        self.reiniciar_juego()

    def reiniciar_juego(self):
        self.todos_sprites = pygame.sprite.Group()
        self.ciudades = pygame.sprite.Group()
        self.balas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()

        # Crear ciudades
        posiciones_ciudades = [ANCHO_PANTALLA // 4, ANCHO_PANTALLA // 2, 3 * ANCHO_PANTALLA // 4]
        for x in posiciones_ciudades:
            ciudad = Ciudad(x)
            self.ciudades.add(ciudad)
            self.todos_sprites.add(ciudad)

        # Crear jugador
        self.jugador = Jugador()
        self.todos_sprites.add(self.jugador)

        # Inicializar vidas (3 vidas)
        self.vidas = 3

        self.ronda = 1
        self.temporizador_enemigos = 0
        self.retraso_enemigos = 2000  # 2 segundos

        # Duración de cada ronda: 1 minuto (60,000 ms)
        self.duracion_ronda = 60 * 1000
        self.inicio_ronda = pygame.time.get_ticks()

        # Tiempo de pausa entre rondas (5 segundos)
        self.tiempo_pausa = 5 * 1000
        self.inicio_pausa = 0

    def manejar_eventos(self):
        pos_mouse = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if self.estado == EstadoJuego.JUGANDO:
                        bala = self.jugador.disparar()
                        if bala:
                            self.balas.add(bala)
                            self.todos_sprites.add(bala)
                    elif self.estado in [EstadoJuego.JUEGO_TERMINADO, EstadoJuego.VICTORIA]:
                        self.estado = EstadoJuego.MENU

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if self.estado == EstadoJuego.MENU:
                    if self.boton_jugar.rect.collidepoint(pos_mouse):
                        self.estado = EstadoJuego.JUGANDO
                        self.reiniciar_juego()
                    elif self.boton_salir.rect.collidepoint(pos_mouse):
                        return False
                    elif self.boton_modo.rect.collidepoint(pos_mouse):
                        self.usar_enemigos_avanzados = not self.usar_enemigos_avanzados
                        if self.usar_enemigos_avanzados:
                            self.boton_modo.texto = "MODO: AVANZADO"
                        else:
                            self.boton_modo.texto = "MODO: NORMAL"

        # Actualizar los botones del menú
        if self.estado == EstadoJuego.MENU:
            self.boton_jugar.actualizar(pos_mouse)
            self.boton_salir.actualizar(pos_mouse)
            self.boton_modo.actualizar(pos_mouse)

        return True

    def actualizar(self):
        ahora = pygame.time.get_ticks()

        if self.estado == EstadoJuego.JUGANDO:
            # Usamos el método update() de Pygame para actualizar todos los sprites
            self.todos_sprites.update()

            # Verificar si ha terminado la ronda actual (1 minuto)
            tiempo_transcurrido = ahora - self.inicio_ronda
            if tiempo_transcurrido >= self.duracion_ronda:
                # Eliminar todos los enemigos actuales
                for enemigo in self.enemigos:
                    enemigo.kill()

                if self.ronda >= 3:
                    self.estado = EstadoJuego.VICTORIA
                else:
                    self.ronda += 1
                    self.estado = EstadoJuego.NUEVA_RONDA
                    self.inicio_pausa = ahora
                    return

            # Generar enemigos
            if ahora - self.temporizador_enemigos > self.retraso_enemigos:
                self.temporizador_enemigos = ahora
                if self.usar_enemigos_avanzados:
                    enemigo = EnemigoAvanzado(list(self.ciudades), self.jugador, self)
                else:
                    enemigo = Enemigo(list(self.ciudades))
                self.enemigos.add(enemigo)
                self.todos_sprites.add(enemigo)

            # Colisiones balas-enemigos
            impactos = pygame.sprite.groupcollide(self.enemigos, self.balas, False, True)

            # Procesar impactos
            for enemigo, balas_impacto in impactos.items():
                if isinstance(enemigo, EnemigoAvanzado):
                    enemigo.recibir_impacto()
                else:
                    enemigo.kill()

            # Colisiones enemigos-ciudades
            impactos_ciudades = pygame.sprite.groupcollide(self.enemigos, self.ciudades, True, True)

            # Si hubo impactos en las ciudades, reducir vidas
            if impactos_ciudades:
                self.vidas -= len(impactos_ciudades)

            # Verificar condiciones de derrota
            if self.vidas <= 0 or not self.ciudades:
                self.estado = EstadoJuego.JUEGO_TERMINADO

        elif self.estado == EstadoJuego.NUEVA_RONDA:
            # Esperar el tiempo de pausa entre rondas
            if ahora - self.inicio_pausa >= self.tiempo_pausa:
                self.estado = EstadoJuego.JUGANDO
                self.inicio_ronda = ahora  # Reiniciar el temporizador de la ronda
                self.temporizador_enemigos = ahora  # Preparar para generar enemigos

    def dibujar(self):
        self.pantalla.fill(NEGRO)

        if self.estado == EstadoJuego.MENU:
            # Dibujar título
            texto = self.fuente.render("DEFENSOR ESPACIAL", True, BLANCO)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 4))
            self.pantalla.blit(texto, rect_texto)

            # Dibujar instrucciones
            texto_instrucciones = self.fuente_pequena.render("Protege tus ciudades de los invasores", True, BLANCO)
            rect_instrucciones = texto_instrucciones.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 4 + 60))
            self.pantalla.blit(texto_instrucciones, rect_instrucciones)

            # Dibujar botones
            self.boton_jugar.dibujar(self.pantalla)
            self.boton_salir.dibujar(self.pantalla)
            self.boton_modo.dibujar(self.pantalla)

        elif self.estado == EstadoJuego.JUGANDO:
            self.todos_sprites.draw(self.pantalla)

            # Mostrar ronda actual
            texto = self.fuente_pequena.render(f"Ronda: {self.ronda}/3", True, BLANCO)
            self.pantalla.blit(texto, (10, 10))

            # Mostrar vidas debajo del contador de rondas
            texto_vidas = self.fuente_pequena.render(f"Vidas: {self.vidas}", True, BLANCO)
            self.pantalla.blit(texto_vidas, (10, 40))  # Posicionado debajo del contador de rondas

            # Mostrar tipo de enemigos
            tipo_enemigos = "Avanzados" if self.usar_enemigos_avanzados else "Normales"
            texto_enemigos = self.fuente_pequena.render(f"Enemigos: {tipo_enemigos}", True, BLANCO)
            self.pantalla.blit(texto_enemigos, (10, 70))  # Posicionado debajo de las vidas

            # Mostrar tiempo restante
            tiempo_transcurrido = pygame.time.get_ticks() - self.inicio_ronda
            tiempo_restante = max(0, self.duracion_ronda - tiempo_transcurrido)
            minutos = tiempo_restante // 60000
            segundos = (tiempo_restante % 60000) // 1000
            texto_tiempo = self.fuente_pequena.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, BLANCO)
            self.pantalla.blit(texto_tiempo, (ANCHO_PANTALLA - 180, 10))

        elif self.estado == EstadoJuego.NUEVA_RONDA:
            self.todos_sprites.draw(self.pantalla)

            texto = self.fuente.render(f"RONDA {self.ronda}", True, AMARILLO)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 50))
            self.pantalla.blit(texto, rect_texto)

            tiempo_restante = (self.tiempo_pausa - (pygame.time.get_ticks() - self.inicio_pausa)) // 1000
            texto = self.fuente_pequena.render(f"Preparando siguiente ronda... {tiempo_restante}", True, BLANCO)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 + 20))
            self.pantalla.blit(texto, rect_texto)

        elif self.estado == EstadoJuego.JUEGO_TERMINADO:
            texto = self.fuente.render("JUEGO TERMINADO", True, ROJO)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
            self.pantalla.blit(texto, rect_texto)

            texto = self.fuente_pequena.render("Presiona ESPACIO para volver al menú", True, BLANCO)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 + 50))
            self.pantalla.blit(texto, rect_texto)

        elif self.estado == EstadoJuego.VICTORIA:
            texto = self.fuente.render("¡VICTORIA!", True, VERDE)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
            self.pantalla.blit(texto, rect_texto)

            texto = self.fuente_pequena.render("Presiona ESPACIO para volver al menú", True, BLANCO)
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 + 50))
            self.pantalla.blit(texto, rect_texto)

        pygame.display.flip()

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FPS)


# Iniciar el juego
if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
    pygame.quit()

