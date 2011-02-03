from random import choice

def pathto(creature, world, goal):
    steps = 256
    
    p1 = world.space.pathing.path_op(creature.location, goal)
    p2 = world.space.pathing.path_op(goal, creature.location)

    path = None
    while True:
        yield _(u'plotting course'), path
        
        if not p1.done and not p2.done:
            p1.iterate(steps)
            p2.iterate(steps)
            continue

        if p1.done:
            path = p1.path
        elif p2.path is not None:
            path = p2.path[::-1][1:] + [goal]

def goto(creature, world, goal):
    for step, path in pathto(creature, world, goal):
        yield step
        if path:
            for location in path:
                yield _(u'travelling')
                world.movecreature(creature, location)
            break

def takeitem(creature, world, item):
    item.reserved = True
    for step in goto(creature, world, item.location):
        yield _(u'{going} to {item}').format(
            going=step, item=item.description())

    if creature.location != item.location:
        return
    
    yield _(u'picking up {item}').format(item=item.description())
    item.reserved = False
    world.removeitem(item)
    item.location = None
    creature.inventory.add(item)

def takefromstockpile(creature, world, pile, itemtype):
    item = pile.find(lambda item: isinstance(item, itemtype))
    item.reserved = True
    for step in goto(creature, world, pile.components[0].location):
        yield _(u'{going} to {stockpile}').format(
            going=step, stockpile=pile.description())

    yield _(u'taking {item} from {stockpile}').format(
        item=item, stockpile=pile)
    item.reserved = False
    world.removeitem(item)
    creature.inventory.add(item)

def acquireitem(creature, world, stocktype, itemtype):
    if creature.player:
        for pile in creature.player.getstockpiles(stocktype):
            if pile.has(itemtype):
                for step in takefromstockpile(creature, world, pile, itemtype):
                    yield step
                if creature.inventory.has(itemtype):
                    break
        else:
            for item in creature.player.unstockpileditems(stocktype):
                if not item.reserved:
                    for step in takeitem(creature, world, item):
                        yield step
                if creature.inventory.has(itemtype):
                    break
    else:
        for item in world.items:
            if not item.reserved:
                for step in takeitem(creature, world, item):
                    yield step
            if creature.inventory.has(itemtype):
                break
            
def discarditem(creature, world, item):
    yield _(u'discarding {item}').format(item=item.description())
    creature.inventory.remove(item)
    item.location = creature.location
    world.additem(item)

def stashitem(creature, world, item):
    if creature.player:
        for pile in creature.player.getstockpiles(item.stocktype):
            if pile.space():
                for step in storeinstockpile(creature, world, pile, item):
                    yield step
                break
        else:
            for step in discarditem(creature, world, item):
                yield step
    else:
        for step in discarditem(creature, world, item):
            yield step

def meander(creature, world):
    adjacent = world.space.pathing.open_adjacent(creature.location)
    if len(adjacent) > 0:
        world.movecreature(creature, choice([a for a in adjacent]))
    
    return _(u'idling')
