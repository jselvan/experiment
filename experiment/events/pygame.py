from collections.abc import Sequence
import pygame
from experiment.events import EventManager, Event

class PygameEventManager(EventManager):
    def post_event(self, event: Event):
        raise NotImplementedError()
    def get_events(self) -> Sequence[Event]:
        event_stack = []
        for pg_event in pygame.event.get():
            event = {}
            event['time'] = pg_event.dict.get('timestamp', pygame.time.get_ticks())
            if pg_event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                event.update(
                    type="mouse_down",
                    x=mouseX,
                    y=mouseY,
                )
                event_stack.append(event)
            elif pg_event.type == pygame.MOUSEBUTTONUP:
                mouseX, mouseY = pygame.mouse.get_pos()
                event.update(
                    type="mouse_up",
                    x=mouseX,
                    y=mouseY,
                )
                event_stack.append(event)
            elif pg_event.type == pygame.MOUSEMOTION:
                mouseX, mouseY = pygame.mouse.get_pos()
                event.update(x=mouseX, y=mouseY)
                if pg_event.buttons[0]:
                    event['type'] = 'mouse_drag'
                else:
                    event['type'] = 'mouse_move'
                event_stack.append(event)
            elif pg_event.type == pygame.QUIT:
                event.update(type="QUIT", do="quit")
                event_stack.append(event)
            elif pg_event.type == pygame.KEYDOWN:
                if pg_event.key == pygame.K_ESCAPE:
                    event.update(type="key_down", key="escape", do="quit")
                    event_stack.append(event)
                if pg_event.key == pygame.K_SPACE:
                    event.update(type="key_down", key="space")
                    event_stack.append(event)
                if pg_event.key == pygame.K_RETURN:
                    event.update(type="key_down", key="enter")
                    event_stack.append(event)
            else:
                continue
        for event in event_stack:
            self.manager.logger.log_event('event', event)
        return event_stack
