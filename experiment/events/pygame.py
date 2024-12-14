from collections.abc import Sequence
import pygame
from experiment.events import EventManager, Event

class PygameEventManager(EventManager):
    def post_event(self, event: Event):
        raise NotImplementedError()
    def get_events(self) -> Sequence[Event]:
        event_stack = []
        for pg_event in pygame.event.get():
            if pg_event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                event = dict(
                    type="mouse_down",
                    x=mouseX,
                    y=mouseY,
                )
                event_stack.append(event)
            elif pg_event.type == pygame.QUIT:
                event = dict(type="QUIT", do="quit")
            elif pg_event.type == pygame.KEYDOWN:
                if pg_event.key == pygame.K_ESCAPE:
                    event = dict(type="key_down", key="escape", do="quit")
                if pg_event.key == pygame.K_SPACE:
                    event = dict(type="key_down", key="space", do="pause")
        return event_stack
