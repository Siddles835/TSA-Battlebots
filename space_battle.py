from lib.window_arena import *
from lib.winobj_ship import *
from typing import List

# update ship (this is where your code goes)

def updateShip1(ship, powerUps, targets):
    import math, time
    from lib.utils import v2
    from lib.winobj_ship import ShipCmd_Shoot, ShipCmd_Thrust, ShipCmd_ThrustLeft, ShipCmd_ThrustRight
    ship.setPlayerName("First L")
    hyp = math.hypot
    def drive(x, y, cap):
        mx, my = ship.window.maxCoordinateX(), ship.window.maxCoordinateY()
        x, y = min(max(float(x), 0.6), mx - 0.6), min(max(float(y), 0.6), my - 0.6)
        dx, dy = x - ship.pos[0], y - ship.pos[1]
        if (d := hyp(dx, dy)) < 0.15: return
        ux, uy, fx, fy = dx / d, dy / d, float(ship.dir[0]), float(ship.dir[1])
        dot = max(-1.0, min(1.0, fx * ux + fy * uy))
        if dot < 0.999:
            ship.queueCommand((ShipCmd_ThrustLeft if ux * fy - uy * fx > 0 else ShipCmd_ThrustRight)(math.degrees(math.acos(dot))))
        ship.queueCommand(ShipCmd_Thrust(min(d, cap)))
    def lead(px, py, vx, vy, slack):
        ax, ay, fx, fy = px, py, float(ship.dir[0]), float(ship.dir[1])
        for _ in range(4):
            dx, dy = ax - ship.pos[0], ay - ship.pos[1]
            d = hyp(dx, dy) or 1
            dot = max(-1.0, min(1.0, (fx * dx + fy * dy) / d))
            wait = (0 if dot >= 0.999 else math.degrees(math.acos(dot)) / ship.shipTurnSpeed) + max(d - 0.5, 0) / 8
            ax, ay = px + vx * wait, py + vy * wait
        dx, dy = ax - ship.pos[0], ay - ship.pos[1]
        off = ax < -0.4 or ay < -0.4 or ax > ship.window.maxCoordinateX() + 0.4 or ay > ship.window.maxCoordinateY() + 0.4
        if off or max(hyp(dx, dy) - 0.5, 0) > ship.ammoMaxRange + slack: return None
        return (dx, dy)
    other = ship.getOther()
    if ship.window.levelTime < 0.3: return
    cmds = ([other.activeCommand] if other and other.activeCommand else []) + (list(other.queuedCommands) if other else [])
    for c in cmds:
        if isinstance(c, ShipCmd_Shoot) and other.ammo > 0:
            m = hyp(c.dir[0], c.dir[1]) or 1
            sdx, sdy, rx, ry = float(c.dir[0]) / m, float(c.dir[1]) / m, ship.pos[0] - other.pos[0], ship.pos[1] - other.pos[1]
            if 0 < rx * sdx + ry * sdy < other.ammoMaxRange + 0.5 and abs(rx * sdy - ry * sdx) < 0.6:
                return drive(ship.pos[0] - sdy * 1.6, ship.pos[1] + sdx * 1.6, 1.8)
    shot = None
    if ship.ammo > 0 and time.time() - ship.timeLastShot > 1:
        for t in targets:
            if t.isDying(): continue
            s = lead(float(t.pos[0]), float(t.pos[1]), float(t.vel[0]), float(t.vel[1]), 0.25)
            if s and (shot is None or hyp(*s) < hyp(*shot)): shot = s
        if cmds and isinstance(cmds[0], ShipCmd_Thrust):
            s = lead(float(other.pos[0]), float(other.pos[1]), float(other.dir[0]) * other.shipMoveSpeed, float(other.dir[1]) * other.shipMoveSpeed, 0)
            if s: shot = s
    if shot: return ship.queueCommand(ShipCmd_Shoot(v2(shot[0], shot[1])))
    best, best_u = None, -1
    for p in powerUps:
        if p.isDying(): continue
        k = str(p.type)
        w = (55 if ship.shipMoveSpeed < 7 else 14) if k == "S" else (42 if ship.ammoMaxRange < 12 else 12) if k == "R" else 25 if k == "P" else (22 + 15 * int(k) if ship.ammo < 1 else 8 + 5 * int(k)) if k.isdigit() else 0
        d = hyp(p.pos[0] - ship.pos[0], p.pos[1] - ship.pos[1]) + 0.5
        if other and hyp(p.pos[0] - other.pos[0], p.pos[1] - other.pos[1]) + 1 < d: w *= 0.45
        if w / d > best_u: best, best_u = p, w / d
    if best: return drive(best.pos[0], best.pos[1], 30 if ship.ammo < 1 else 3.6)
    live = [t for t in targets if not t.isDying()]
    if not live: return drive(ship.window.maxCoordinateX() / 2, ship.window.maxCoordinateY() / 2, 3)
    t = min(live, key=lambda t: hyp(t.pos[0] - ship.pos[0], t.pos[1] - ship.pos[1]))
    drive(t.pos[0] + t.vel[0], t.pos[1] + t.vel[1], 3.2)




####################################################################################################
############################## DO NOT MODIFY  METHODS BELOW THIS LINE ##############################
########################## EXCEPT TO REMOVE TUTORIAL GAME CONFIG ARGUMENT  #########################
####################################################################################################
WindowArena(userCode1 = updateShip1,
            gameConfig = WindowArenaConfig.SPACE_BATTLE,
            windowTitle = "TSA@RHS: Space Battle!").runGameLoop()