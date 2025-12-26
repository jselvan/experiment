from collections.abc import Sequence
import pygame
from experiment.events import EventManager, Event

class PygameEventManager(EventManager):
    def get_events(self) -> Sequence[Event]:
        event_stack = super().get_events()
        for pg_event in pygame.event.get():
            event = {}
            event['time'] = pg_event.dict.get('timestamp', pygame.time.get_ticks())
            numbers = [
                pygame.K_1, pygame.K_3, pygame.K_5
            ] 
            if pg_event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                event.update(
                    type="mouse_down",
                    x=mouseX,
                    y=mouseY,
                )
            elif pg_event.type == pygame.MOUSEBUTTONUP:
                mouseX, mouseY = pygame.mouse.get_pos()
                event.update(
                    type="mouse_up",
                    x=mouseX,
                    y=mouseY,
                )
            elif pg_event.type == pygame.MOUSEMOTION:
                mouseX, mouseY = pygame.mouse.get_pos()
                event.update(x=mouseX, y=mouseY)
                if pg_event.buttons[0]:
                    event['type'] = 'mouse_drag'
                else:
                    event['type'] = 'mouse_move'
            elif pg_event.type == pygame.QUIT:
                event.update(type="QUIT", do="quit")
            elif pg_event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(pg_event.key)
                if key_name in self.manager.hotkeys:
                    action = self.manager.hotkeys[key_name]
                    event.update(type="key_down", key=key_name, **action)
                else:
                    event.update(type="key_down", key=key_name)
            else:
                continue
            event_stack.append(event)
        for event in event_stack:
            self.manager.logger.log_event('event', event)
        return event_stack
