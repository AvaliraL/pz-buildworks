# Known poor interaction: phuninteriors vehicle interiors vs our walk-through pieces

Status: accepted for now (user, 2026-11-08). Partly fixed:
- Overlay CORNERS (39, plus the paused 43/44) now build as a dismantlable IsoThumpable
  (`canPassThrough: false`, `isThumpable: false`), so vanilla Dismantle works on them in interiors.
  Their N/W edges already carry walls, so the thumpable's edge collision blocks nothing new.
  Built and checked; not yet tested in game.
- Still props, and still not removable inside interiors: pillars and end caps (they can stand at an
  open wall end), and door frames.

Inside a hardened PhunInteriors room, `PhunInteriors/client_guards.lua` blocks the sledgehammer
(`ISDestroyStuffAction`) and the build-menu destroy cursor (`ISDestroyCursor`) for every object, so
the only way left to remove a build is vanilla Dismantle. Dismantle needs an IsoThumpable.

KBW builds every walk-through stage (`canPassThrough: true` / `isProp`) as a moveable prop or a plain
IsoObject, never an IsoThumpable (`WallFinishes.buildsAsProp` and `KBWBuildingObject.lua`, ~1505-1530).
So inside an interior these pieces cannot be removed:

- pillars (21, 40)
- door frames (21: `isThumpable` + `canPassThrough`, so they still build as props)
- overlay corners and end caps (39; also the paused 43/44)

Plain overlay panels work, through KBW's "Remove %1" attached-sprite option. Outside interiors all
of these can be removed normally.

Possible fix if it matters later: a "Dismantle" option for objects with `modData.KBW` that are not
IsoThumpable. It would use a client -> server command, refund part of the cost, and still leave the
room's base walls protected, because they carry no KBW modData. Making these pieces thumpable would
make them block movement, so that isn't a good alternative.
