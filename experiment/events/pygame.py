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
                if pg_event.key == pygame.K_ESCAPE:
                    event.update(type="key_down", key="escape", do="quit")
                elif pg_event.key == pygame.K_SPACE:
                    event.update(type="key_down", key="space")
                elif pg_event.key == pygame.K_RETURN:
                    event.update(type="key_down", key="enter")
                elif pg_event.key == pygame.K_r:
                    event.update(type="key_down", key="r", do="reward")
                elif pg_event.key in numbers:
                    if pg_event.key == pygame.K_1:
                        key = 1
                    elif pg_event.key == pygame.K_3:
                        key = 3
                    else:
                        key = 5
                    event.update(type="key_down", key=key, do="reward_pulses")
                else:
                    event.update(type="key_down", key=pg_event.key)
            else:
                continue
            event_stack.append(event)
        for event in event_stack:
            self.manager.logger.log_event('event', event)
        return event_stack
