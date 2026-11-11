from lib.window_arena import *
from lib.winobj_ship import *
from typing import List

# update ship (this is where your code goes)

def updateShip1(ship, powerUps, targets):
    import math
    import time
    from lib.utils import v2
    from lib.winobj_ship import (
        ShipCmd_Shoot,
        ShipCmd_Thrust,
        ShipCmd_ThrustLeft,
        ShipCmd_ThrustRight
    )
    ship.setPlayerName("Sidhaanth K")

    def distance(x, y):
        return math.hypot(x, y)

    def drive_to(x, y, cap):
        max_x = ship.window.maxCoordinateX()
        max_y = ship.window.maxCoordinateY()
        x = min(max(float(x), 0.6), max_x - 0.6)
        y = min(max(float(y), 0.6), max_y - 0.6)
        dx = x - ship.pos[0]
        dy = y - ship.pos[1]
        d = distance(dx, dy)
        if d < 0.15:
            return
        ux = dx / d
        uy = dy / d
        fx = float(ship.dir[0])
        fy = float(ship.dir[1])
        dot = max(-1.0, min(1.0, fx * ux + fy * uy))

        if dot < 0.999:
            cross = ux * fy - uy * fx
            angle = math.degrees(math.acos(dot))
            if cross > 0:
                ship.queueCommand(ShipCmd_ThrustLeft(angle))
            else:
                ship.queueCommand(ShipCmd_ThrustRight(angle))

        ship.queueCommand(ShipCmd_Thrust(min(d, cap)))

    def get_shot_direction(px, py, vx, vy, slack):
        aim_x = px
        aim_y = py
        fx = float(ship.dir[0])
        fy = float(ship.dir[1])

        for _ in range(4):
            dx = aim_x - ship.pos[0]
            dy = aim_y - ship.pos[1]
            d = distance(dx, dy) or 1

            dot = (fx * dx + fy * dy) / d
            dot = max(-1.0, min(1.0, dot))
            turn_time = 0

            if dot < 0.999:
                turn_time = math.degrees(math.acos(dot)) / ship.shipTurnSpeed
            move_time = max(d - 0.5, 0) / 8
            total_time = turn_time + move_time
            aim_x = px + vx * total_time
            aim_y = py + vy * total_time
        dx = aim_x - ship.pos[0]
        dy = aim_y - ship.pos[1]
        max_x = ship.window.maxCoordinateX()
        max_y = ship.window.maxCoordinateY()

        outside = (
            aim_x < -0.4 or
            aim_y < -0.4 or
            aim_x > max_x + 0.4 or
            aim_y > max_y + 0.4
        )

        if outside:
            return None
        if max(distance(dx, dy) - 0.5, 0) > ship.ammoMaxRange + slack:
            return None
        return dx, dy

    other = ship.getOther()
    if ship.window.levelTime < 0.3:
        return
    commands = []

    if other:
        if other.activeCommand:
            commands.append(other.activeCommand)

        commands.extend(list(other.queuedCommands))

    for command in commands:
        if isinstance(command, ShipCmd_Shoot) and other.ammo > 0:
            d = distance(command.dir[0], command.dir[1]) or 1
            sx = float(command.dir[0]) / d
            sy = float(command.dir[1]) / d
            rx = ship.pos[0] - other.pos[0]
            ry = ship.pos[1] - other.pos[1]
            forward = rx * sx + ry * sy
            sideways = abs(rx * sy - ry * sx)

            if (
                0 < forward < other.ammoMaxRange + 0.5
                and sideways < 0.6
            ):
                return drive_to(
                    ship.pos[0] - sy * 1.6,
                    ship.pos[1] + sx * 1.6,
                    1.8
                )
    shot = None

    if ship.ammo > 0 and time.time() - ship.timeLastShot > 1:
        for target in targets:
            if target.isDying():
                continue

            direction = get_shot_direction(
                float(target.pos[0]),
                float(target.pos[1]),
                float(target.vel[0]),
                float(target.vel[1]),
                0.25
            )

            if direction:
                if shot is None or distance(*direction) < distance(*shot):
                    shot = direction

        if commands and isinstance(commands[0], ShipCmd_Thrust):
            direction = get_shot_direction(
                float(other.pos[0]),
                float(other.pos[1]),
                float(other.dir[0]) * other.shipMoveSpeed,
                float(other.dir[1]) * other.shipMoveSpeed,
                0
            )
            if direction:
                shot = direction
                
    if shot:
        return ship.queueCommand(
            ShipCmd_Shoot(v2(shot[0], shot[1]))
        )
    best_powerup = None
    best_score = -1

    for powerup in powerUps:
        if powerup.isDying():
            continue
        power_type = str(powerup.type)

        if power_type == "S":
            value = 55 if ship.shipMoveSpeed < 7 else 14
        elif power_type == "R":
            value = 42 if ship.ammoMaxRange < 12 else 12
        elif power_type == "P":
            value = 25
        elif power_type.isdigit():
            number = int(power_type)
            if ship.ammo < 1:
                value = 22 + 15 * number
            else:
                value = 8 + 5 * number
        else:
            value = 0

        d = distance(
            powerup.pos[0] - ship.pos[0],
            powerup.pos[1] - ship.pos[1]
        ) + 0.5

        if other:
            opponent_distance = distance(
                powerup.pos[0] - other.pos[0],
                powerup.pos[1] - other.pos[1]
            ) + 1
            if opponent_distance < d:
                value *= 0.45

        score = value / d
        if score > best_score:
            best_powerup = powerup
            best_score = score
            
    if best_powerup:
        speed = 30 if ship.ammo < 1 else 3.6

        return drive_to(
            best_powerup.pos[0],
            best_powerup.pos[1],
            speed
        )
    live_targets = []

    for target in targets:
        if not target.isDying():
            live_targets.append(target)

    if not live_targets:
        return drive_to(
            ship.window.maxCoordinateX() / 2,
            ship.window.maxCoordinateY() / 2,
            3
        )
    closest_target = min(
        live_targets,
        key=lambda target: distance(
            target.pos[0] - ship.pos[0],
            target.pos[1] - ship.pos[1]
        )
    )
    drive_to(
        closest_target.pos[0] + closest_target.vel[0],
        closest_target.pos[1] + closest_target.vel[1],
        3.2
    )





####################################################################################################
############################## DO NOT MODIFY  METHODS BELOW THIS LINE ##############################
########################## EXCEPT TO REMOVE TUTORIAL GAME CONFIG ARGUMENT  #########################
####################################################################################################
WindowArena(userCode1 = updateShip1,
            gameConfig = WindowArenaConfig.SPACE_BATTLE,
            windowTitle = "TSA@RHS: Space Battle!").runGameLoop()