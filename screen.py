from pygame import event, gfxdraw, key, mouse, Rect, Surface
from pygame.locals import *
from pygame.mixer import *
from pygame.sprite import *

from data import Barrel, Beverage, Corpse, Entity, Stockpile
from glyphs import GlyphGraphics

class GameScreen(object):
    def __init__(self, game, font, zoom):
        self.game = game

        self.zoom = zoom

        self.sprites = LayeredDirty()

        self.scale(font)
        
        self.selection = []
        
        self.level = 64

        self.stepsound = Sound('38874__swuing__footstep_grass.wav')

    def hexpoints(self):
        return [(self.zoom.height/3,self.zoom.height),
                (0,self.zoom.height/2),
                (self.zoom.height/3,0),
                (self.zoom.width,0),
                (self.zoom.width+self.zoom.height/3,self.zoom.height/2),
                (self.zoom.width,self.zoom.height)]

    def scale(self, font):
        self.font = font
            
        self.graphics = GlyphGraphics(self.font)

        self.air = Entity('air')
        self.button = Entity('button')
        self.ground = Entity('ground')

        self.hex_image = Surface((self.zoom.width+self.zoom.height/3,
                                  self.zoom.height+1),
                            flags=SRCALPHA)
        gfxdraw.polygon(self.hex_image, self.hexpoints(), (0, 0, 0))

        self.hex_fill = Surface(self.hex_image.get_size(), flags=SRCALPHA)
        gfxdraw.filled_polygon(self.hex_fill, self.hexpoints(), (0,0, 0, 255))

        self.sky = self.hex_fill.copy()
        self.sky.fill((0, 85, 85), special_flags=BLEND_ADD)

        self.designation = self.hex_fill.copy()
        self.designation.fill((0, 0, 0, 85), special_flags=BLEND_RGBA_MULT)
        self.designation.fill((85, 85, 0), special_flags=BLEND_ADD)

        self.grid_image = Surface(self.hex_image.get_size(), flags=SRCALPHA)
        if False: # set true to show grid
            self.grid_image.blit(self.hex_image, (0, 0))
            self.grid_image.fill((16,16,16), special_flags=BLEND_ADD)

        self.sprites.empty()

        self.mouse_sprite = DirtySprite()
        self.mouse_sprite.image = Surface(self.hex_image.get_size(),
                                          flags=SRCALPHA)
        self.mouse_sprite.image.blit(self.hex_image, (0,0))
        self.mouse_sprite.image.fill((255,255,0), special_flags=BLEND_ADD)
        self.mouse_sprite.rect = self.mouse_sprite.image.get_rect()

        self.selection_sprite = None

        self.entity_sprites = {}

    def makebackground(self):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                location = self.tile_location((x,y,self.level))
                tile = self.game.world.space[(self.offset[0] + x,
                                              self.offset[1] + y,
                                              self.level)]
                if tile is None:
                    continue
                if tile.is_passable():
                    if self.level > 0:
                        foundation = self.game.world.space[(self.offset[0] + x,
                                                            self.offset[1] + y,
                                                            self.level - 1)]
                        if not foundation.is_passable():
                            if foundation.kind is None:
                                dirt = self.graphics[self.ground][foundation.varient].copy()
                                dirt.fill(foundation.color, special_flags=BLEND_ADD)

                                self.background.blit(dirt, location)
                                if (self.offset[0] + x, self.offset[1] + y,
                                    self.level -1) in self.game.world.designations:
                                    self.background.blit(self.designation,
                                                         (location[0]-self.zoom.height/3,
                                                          location[1]))
                            else:
                                air = self.graphics[self.air][0].copy()
                                air.fill(foundation.color, special_flags=BLEND_ADD)

                                self.background.blit(air, location)
                        else:
                            drawn = False
                            if self.level > 1:
                                below = self.game.world.space[(self.offset[0]+x,
                                                               self.offset[1]+y,
                                                               self.level-2)]
                                if not below.is_passable() and below.kind is None:
                                    air = self.graphics[self.air][0].copy()
                                    air.fill(below.color, special_flags=BLEND_ADD)
                                    self.background.blit(air, location)
                                    drawn = True

                            if not drawn:
                                self.background.blit(self.sky,
                                                     (location[0]-self.zoom.height/3,
                                                      location[1]))
                                
                elif tile.kind is not None:
                    if tile.kind == 'tree-trunk':
                        image = self.graphics[tile][0].copy()
                        image.fill(tile.color, special_flags=BLEND_ADD)
                        image.fill((48,48,48), special_flags=BLEND_ADD)
                        exterior = self.graphics[tile][1].copy()
                        exterior.fill(tile.color, special_flags=BLEND_ADD)
                        image.blit(exterior, (0,0))
                        rings = self.graphics[tile][2].copy()
                        rings.fill(tile.color, special_flags=BLEND_ADD)
                        image.blit(rings, (0,0))
                        self.background.blit(image, location)
                    else:
                        image = self.graphics[tile][tile.varient].copy()
                        image.fill(tile.color, special_flags=BLEND_ADD)
                        self.background.blit(image, location)

                else:
                    if tile.revealed:
                        image = self.hex_fill.copy()
                        image.fill(tile.color, special_flags=BLEND_ADD)
                        self.background.blit(image,
                                             (location[0]-self.zoom.height/3,
                                              location[1]))

                    if (self.offset[0] + x, self.offset[1] + y,
                          self.level) in self.game.world.designations:
                        self.background.blit(self.designation,
                                             (location[0]-self.zoom.height/3,
                                              location[1]))


                self.background.blit(self.grid_image,
                                     (location[0]-self.zoom.height/3,location[1]))

    def location_tile(self, c):
        px, py = c
        x = (px - self.zoom.width/2)/self.zoom.width
        return x, (py - self.zoom.height/2 - (x&1) * self.zoom.height/2)/self.zoom.height

    def tile_location(self, c):
        x, y, z = c
        return (self.zoom.width/2 + x * self.zoom.width,
                self.zoom.height/2 + y * self.zoom.height +
                ((x+self.offset[0])&1) * self.zoom.height/2)

    def resize(self, size):
        self.background = Surface(size, flags=SRCALPHA)
        self.background.fill((0,0,0))

        self.dimensions = self.location_tile(size)

        try:
            self.offset
        except AttributeError:            
            remainder = [self.game.dimensions[i] - self.dimensions[i]
                         for i in range(2)]
            self.offset = tuple([r/2 if r > 0 else 0 for r in remainder])
        
        self.makebackground()

    def visible(self, location):
        return location and all([self.offset[i] <= location[i] < self.offset[i] + self.dimensions[i]
                    for i in range(2)]) and location[2] == self.level

    def update(self, entities, pos, descs):
        moved = False

        for entity in entities:
            if isinstance(entity, Stockpile):
                self.updatestockpile(entity, pos, descs)
                continue

            described = False
            if self.selection and entity.location in self.selection:
                descs.append(entity.description())
                described = True
            
            if entity.location is None or not self.visible(entity.location):
                if entity in self.entity_sprites:
                    self.sprites.remove(self.entity_sprites[entity])
                    del self.entity_sprites[entity]
            elif entity not in self.entity_sprites:                    
                sprite = DirtySprite()

                if isinstance(entity, Corpse):
                    image = self.graphics[entity.origins][0].copy()
                else:
                    image = self.graphics[entity][0].copy()
                    
                image.fill(entity.color, special_flags=BLEND_ADD)
                
                sprite.image = Surface(image.get_size())
                sprite.image.fill((0,0,0))
                sprite.image.blit(image, (0,0))
                x, y = self.tile_location([entity.location[i] - self.offset[i]
                                           for i in range(2)] +
                                          [entity.location[2]])
                sprite.rect = sprite.image.get_rect().move(x, y)
                self.sprites.add(sprite)

                self.entity_sprites[entity] = sprite

            if entity in self.entity_sprites:
                sprite = self.entity_sprites[entity]
                x, y = self.tile_location([entity.location[i] - self.offset[i]
                                           for i in range(2)] +
                                          [entity.location[2]])
                
                if sprite.rect.topleft != (x,y):
                    sprite.rect.topleft = (x,y)
                    moved = True

                if not described and Rect(x, y,
                                          self.zoom.width,
                                          self.zoom.height).collidepoint(pos):
                    descs.append(entity.description())
                    described = True

        return moved

    def updatestockpile(self, stockpile, pos, descs):
        locations = []
        for component in stockpile.components:
            if self.visible(component.location):
                locations.append(self.tile_location(
                    [component.location[i] - self.offset[i] for i in range(2)] +
                    [component.location[2]]))

        if stockpile in self.entity_sprites:
            changed = stockpile.changed

            if not changed:
                changed = (len(locations) !=
                           len(self.entity_sprites[stockpile].locations) or
                           any([locations[i] !=
                                self.entity_sprites[stockpile].locations[i]
                                for i in range(len(locations))]))

            if changed:
                self.sprites.remove(self.entity_sprites[stockpile])
                del self.entity_sprites[stockpile]
            stockpile.changed = False

        described = False
        if self.selection and any([c.location in self.selection
                                   for c in stockpile.components]):
            descs.append(stockpile.description())
            described = True
        
        if locations and stockpile not in self.entity_sprites:                    

            sprite = DirtySprite()

            image = self.graphics[stockpile][0].copy()
                
            image.fill(stockpile.color, special_flags=BLEND_ADD)
            
            x, y = tuple([min([p[i] for p in locations])
                          for i in range(2)])
            size = tuple([max([p[i] for p in locations]) - (x,y)[i] +
                          (self.zoom.width, self.zoom.height)[i]
                          for i in range(2)])
            
            sprite.image = Surface(size)
            sprite.image.fill((0,0,0))

            items = [item for item in stockpile.contents]
            
            for px,py in locations:
                sprite.image.blit(image, (px-x,py-y))
                
                if items:
                    item = items[0]
                    
                    if isinstance(item, Corpse):
                        itemimage = self.graphics[item.origins][0].copy()
                    else:
                        itemimage = self.graphics[item][0].copy()
                        
                    itemimage.fill(item.color, special_flags=BLEND_ADD)
                    
                    sprite.image.blit(itemimage, (px-x,py-y))
                    
                    items = items[1:]

                if not described and Rect(px-x, py-y,
                                          self.zoom.width,
                                          self.zoom.height).collidepoint(pos):
                    descs.append(stockpile.description())
                    described = True
                    
            sprite.rect = sprite.image.get_rect().move(x, y)
            sprite.locations = locations
            self.sprites.add(sprite)

            self.entity_sprites[stockpile] = sprite

        if stockpile in self.entity_sprites:                    
            sprite = self.entity_sprites[stockpile]

            x, y = tuple([min([p[i] for p in locations])
                          for i in range(2)])

            if sprite.rect.topleft != (x,y):
                sprite.rect.topleft = (x,y)

            for px,py in locations:
                if Rect(px, py,
                        self.zoom.width, self.zoom.height).collidepoint(pos):
                    descs.append(stockpile.description())

    def mousepos(self, pos = None):
        if pos is None:
            pos = mouse.get_pos()
        else:
            mouse.set_pos(pos)
        tile = self.location_tile(pos)
        if not (0 <= tile[0] < self.dimensions[0] and
                0 <= tile[1] < self.dimensions[1]):
            tile = None
        return pos, tile

    def clamp(self, value, limits):
        if value < limits[0]:
            return limits[0], value - limits[0]
        elif value > limits[1]:
            return limits[1], value - limits[1]
        else:
            return value, 0

    def scroll(self, axis, amount):
        size = self.zoom.width if axis == 0 else self.zoom.height

        pos, tile = self.mousepos()

        while (tile is not None and
               ((amount < 0 and
                 tile[axis] + self.offset[axis] >
                 self.game.dimensions[axis] - self.dimensions[axis]/2) or
                (amount > 0 and
                 tile[axis] + self.offset[axis] <
                 self.dimensions[axis]/2))):
            pos, tile = self.mousepos(tuple([pos[i] +
                                             (size * amount/abs(amount)
                                              if i == axis else 0)
                                             for i in range(2)]))
            amount -= amount/abs(amount)

        dest, remainder = self.clamp(
            self.offset[axis] + amount,
            (0, self.game.dimensions[axis] - self.dimensions[axis]))
        
        self.offset = tuple([dest if i == axis else self.offset[i]
                             for i in range(2)])

        while tile is not None and ((remainder < 0 and 0 < tile[axis]) or
               (remainder > 0 and tile[axis] < self.dimensions[axis]-1)):
            pos, tile = self.mousepos(tuple([pos[i] +
                                             (size * remainder/abs(remainder)
                                              if i == axis else 0)
                                             for i in range(2)]))
            remainder -= remainder/abs(remainder)

        return pos, tile

    def arefloor(self, locations):
        return all([self.game.world.space[location].is_passable() and
                    location[2] > 0 and
                    not self.game.world.space[
                        location[0:2] + (location[2]-1,)].is_passable()
                    for location in locations])

    def arewall(self, locations):
        return all([not self.game.world.space[location].is_passable()
                    for location in locations])

    def designate(self, tile):
        x, y, z = tile
        target = self.game.world.space[(x,y,z)]
        if target.is_passable() and z > 0:
            z -= 1
            target = self.game.world.space[(x,y,z)]
        if not target.is_passable():
            self.game.world.designations.append((x,y,z))
            self.makebackground()

    def updateselection(self):
        if self.selection:
            locations = [self.tile_location((p[0] - self.offset[0],
                                             p[1] - self.offset[1],
                                             p[2]))
                         for p in self.selection
                         if self.visible(p)]

            if (not self.selection_sprite or
                len(self.selection_sprite.locations) != len(locations) or
                any([self.selection_sprite.locations[i] != locations[i]
                     for i in range(len(locations))])):
                
                if self.selection_sprite in self.sprites:
                    self.sprites.remove(self.selection_sprite)
                    self.selection_sprite = None

                if locations:
                    self.selection_sprite = DirtySprite()
                    self.selection_sprite.locations = locations
                    
                    x, y = [min([p[i] for p in locations]) for i in range(2)]
                    size = [max([p[i] for p in locations]) - (x,y)[i] +
                            (self.zoom.width+self.zoom.height/3,
                             self.zoom.height+1)[i]
                            for i in range(2)]

                    self.selection_sprite.image = Surface(size, flags=SRCALPHA)

                    for p in self.selection_sprite.locations:
                        self.selection_sprite.image.blit(self.hex_image,
                                                         (p[0]-x,p[1]-y))
                        
                    self.selection_sprite.image.fill((255,0,0),
                                                     special_flags=BLEND_ADD)
                    self.selection_sprite.rect = self.mouse_sprite.image.get_rect()
                    self.selection_sprite.rect.move_ip(x - self.zoom.height/3, y)

                    self.sprites.add(self.selection_sprite, layer=1)
                
            if self.selection_sprite:                    
                x, y = tuple([min([p[i] for p in locations])
                              for i in range(2)])

                x -= self.zoom.height/3

                if self.selection_sprite.rect.topleft != (x,y):
                    self.selection_sprite.rect.topleft = (x,y)
                    
        elif self.selection_sprite:
            self.sprites.remove(self.selection_sprite)
            self.selection_sprite = None

    def designateselection(self):
        for tile in self.selection:
            self.designate(tile)

    def makestockpile(self):
        self.game.world.addstockpile(Stockpile(self.selection, [Beverage.stocktype]))

    def drawbutton(self, surface, title, button_loc, handler):
        outlines = self.graphics[self.button]
        text = self.font.render(' ' + title + ' ', True, (255,255,255))
        
        w = 0
        while w * outlines[0].get_width() < text.get_width():
            w += 1
        h = 0
        while h * outlines[0].get_height() < text.get_height():
            h += 1

        button = Surface(((w+2)*outlines[0].get_width(),
                          (h+2)*outlines[0].get_height()),
                         flags=SRCALPHA)
        
        button.blit(outlines[0], (0,0))
        button.blit(outlines[2], ((w+1)*outlines[0].get_width(),0))
        button.blit(outlines[4], ((w+1)*outlines[0].get_width(),
                                  (h+1)*outlines[0].get_height()))
        button.blit(outlines[6], (0,(h+1)*outlines[0].get_height()))
        
        for i in range(w):
            button.blit(outlines[1], ((i+1)*outlines[0].get_width(),0))
            button.blit(outlines[5], ((i+1)*outlines[0].get_width(),
                                      (h+1)*outlines[0].get_height()))
        for i in range(h):
            button.blit(outlines[3], ((w+1)*outlines[0].get_width(),
                                      (i+1)*outlines[0].get_height()))
            button.blit(outlines[7], (0,(i+1)*outlines[0].get_height()))

        button.fill((255,255,255), special_flags=BLEND_ADD)
        
        button.blit(text, outlines[0].get_size())

        button_loc = button_loc[0], button_loc[1] - button.get_height()

        surface.blit(button, button_loc)

        self.buttonhandlers[(button_loc, button.get_size())] = handler

        return button_loc

    def handle(self, e):
        pos, tile = self.mousepos()
        
        if e.type == KEYDOWN:
            pressed = key.get_pressed()
            shifted = pressed[K_LSHIFT] or pressed[K_RSHIFT]
            scroll = 10 if shifted else 1
                
            if e.key == K_UP:
                pos, tile = self.scroll(1, -scroll)                                        
                self.makebackground()
                
            elif e.key == K_DOWN:
                pos, tile = self.scroll(1, scroll)
                self.makebackground()
                
            elif e.key == K_LEFT:
                pos, tile = self.scroll(0, -scroll)
                self.makebackground()
                
            elif e.key == K_RIGHT:
                pos, tile = self.scroll(0, scroll)
                self.makebackground()
                
            elif e.unicode == '>':
                self.level = max(self.level-1, 0)
                self.makebackground()
            elif e.unicode == '<':
                self.level = min(self.level+1, self.game.dimensions[2])
                self.makebackground()
                
            elif e.unicode == 'd':
                import pdb
                pdb.set_trace()
                
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                if tile is not None:
                    abstile = (tile[0] + self.offset[0],
                               tile[1] + self.offset[1],
                               self.level)
                    if self.selection:
                        if abstile in self.selection:
                            self.selection.remove(abstile)
                        elif any([(x,y,self.level) in self.selection
                                  for x,y in
                                  self.game.world.space.pathing.adjacent_xy(
                                      abstile[0:2])]):
                            self.selection.append(abstile)
                        else:
                            self.selection = [abstile]
                    else:
                        self.selection.append(abstile)
                else:
                    for r in self.buttonhandlers:
                        if Rect(r[0],r[1]).collidepoint(pos):
                            self.buttonhandlers[r]()

    def draw(self, surface):
        pos, tile = self.mousepos()

        if self.game.world.space.changed:
            self.makebackground()
            self.game.world.space.changed = False

        descs = []
        creature_moved = False

        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                this = self.game.world.space[(self.offset[0] + x,
                                              self.offset[1] + y,
                                              self.level)]
                if this:
                    creature_moved = self.update(this.creatures,
                                                 pos, descs) or creature_moved
                    self.update(this.items[0:1], pos, descs)

        self.update(self.game.world.stockpiles, pos, descs)

        for entity in self.entity_sprites.keys():
            if ((isinstance(entity, Stockpile) and
                 entity not in self.game.world.stockpiles) or
                (not isinstance(entity, Stockpile) and
                 not self.visible(entity.location))):
                self.sprites.remove(self.entity_sprites[entity])
                del self.entity_sprites[entity]

        self.updateselection()

        if tile is not None:
            if self.mouse_sprite not in self.sprites:
                self.sprites.add(self.mouse_sprite, layer=2)
            self.mouse_sprite.rect.topleft = self.tile_location(
                tile + (self.level,))
            self.mouse_sprite.rect.move_ip(-self.zoom.height/3, 0)

            mouse.set_visible(False)
        else:
            if self.mouse_sprite in self.sprites:
                self.sprites.remove(self.mouse_sprite)

            mouse.set_visible(True)

        self.sprites.clear(surface, self.background)
        self.sprites.draw(surface)

        info_loc = self.tile_location((self.dimensions[0]+1,0,self.level))
        if self.offset[0]&1:
            info_loc = info_loc[0], info_loc[1] - self.zoom.height/2
        surface.fill((0,0,0), Rect(info_loc, surface.get_size()))
        for d in descs:
            line = self.font.render(d, True, (255,255,255))
            surface.blit(line, info_loc)
            info_loc = (info_loc[0], info_loc[1] + line.get_height())

        self.buttonhandlers = {}
        button_loc = self.tile_location((self.dimensions[0]+1,
                                         self.dimensions[1]+1,
                                         self.level))
        if self.offset[0]&1:
            button_loc = button_loc[0], button_loc[1] - self.zoom.height/2
        if self.selection:
            arefloor = self.arefloor(self.selection)
            if arefloor or self.arewall(self.selection):
                button_loc = self.drawbutton(surface, _('Dig'), button_loc, self.designateselection)
            if (arefloor and all([self.game.world.space[loc].is_passable()
                                  for loc in self.selection]) and
                all([comp.location not in self.selection
                     for pile in self.game.world.stockpiles
                     for comp in pile.components])):
                button_loc = self.drawbutton(surface, _('Stockpile'), button_loc, self.makestockpile)
                     

        if creature_moved:
            self.stepsound.play()

        if self.game.done:
            self.game = None
            mouse.set_visible(True)
            return None
        else:
            return self
