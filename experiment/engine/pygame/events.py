from experiment.events.base import EventSource
import pygame
from experiment.events.types import MouseDownEvent, MouseUpEvent, MouseDragEvent, KeyDownEvent, QuitEvent


class PygameEventSource(EventSource):
    def poll(self):
        events = pygame.event.get()
        for event in events:
            if not self.bus:
                continue
            # convert pygame events to typed events
            if event.type == pygame.QUIT:
                # mark quit events with the 'do' action
                self.bus.publish(QuitEvent(do='quit'))
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = (float(event.pos[0]), float(event.pos[1]))
                self.bus.publish(MouseDownEvent(pos=pos, button=event.button))
                continue
            if event.type == pygame.MOUSEBUTTONUP:
                pos = (float(event.pos[0]), float(event.pos[1]))
                self.bus.publish(MouseUpEvent(pos=pos, button=event.button))
                continue
            if event.type == pygame.MOUSEMOTION:
                pos = (float(event.pos[0]), float(event.pos[1]))
                rel = (float(event.rel[0]), float(event.rel[1]))
                # event.buttons is a tuple of button states
                buttons = tuple(int(b) for b in getattr(event, 'buttons', (0,0,0)))
                self.bus.publish(MouseDragEvent(pos=pos, rel=rel, buttons=buttons))
                continue
            if event.type == pygame.KEYDOWN:
                # convert key and mod to strings for portability
                key_name = pygame.key.name(event.key)
                mod_mask = getattr(event, 'mod', 0)
                mods = []
                if mod_mask & pygame.KMOD_SHIFT:
                    mods.append('shift')
                if mod_mask & pygame.KMOD_CTRL:
                    mods.append('ctrl')
                if mod_mask & pygame.KMOD_ALT:
                    mods.append('alt')
                if mod_mask & pygame.KMOD_META:
                    mods.append('meta')
                if mod_mask & pygame.KMOD_CAPS:
                    mods.append('caps')
                if mod_mask & pygame.KMOD_NUM:
                    mods.append('num')
                mod_str = '+'.join(mods) if mods else None
                self.bus.publish(KeyDownEvent(key=key_name, mod=mod_str))
                continue
            # fallback: publish the raw event for compatibility
            self.bus.publish(event)
