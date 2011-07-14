# -*- coding: utf-8 -*-
import random
import sys
import string
import math

# Width and height of the playing field.
SIZE = 31

# Number of children on each team.
CCOUNT = 4

# Constants for the objects in each cell of the field
GROUND_EMPTY = 0  # Just powdered snow in this space.
GROUND_TREE = 1   # A tree in this space
GROUND_S = 2      # A small snowball in this space
GROUND_M = 3      # A medium snowball in this space
GROUND_MS = 4     # A small snowball on a medium one
GROUND_L = 5      # A large snowball in this space
GROUND_LM = 6     # A medium snowball on a large one.
GROUND_LS = 7     # A small snowball on a large one.
GROUND_SMR = 8    # A red Snowman in this space
GROUND_SMB = 9    # A blue Snowman in this space

# Constants for the things a child can be holding
HOLD_EMPTY = 0    # Child is holding nothing
HOLD_P1 = 1       # Child is holding one unit of powdered snow
HOLD_P2 = 2       # Child is holding two units of powdered snow
HOLD_P3 = 3       # Child is holding three units of powdered snow
HOLD_S1 = 4       # Child is holding one small snowball.
HOLD_S2 = 5       # Child is holding two small snowballs.
HOLD_S3 = 6       # Child is holding three small snowballs.
HOLD_M = 7        # Child is holding one medium snowball.
HOLD_L = 8        # Child is holding one large snowball.

# Constant for the red player color
RED = 0

# Constant for the blue player color
BLUE = 1

# Height for a standing child.
STANDING_HEIGHT = 9

# Height for a crouching child.
CROUCHING_HEIGHT = 6

# Maximum Euclidean distance a child can throw.
THROW_LIMIT = 24

# Snow capacity limit for a space.
MAX_PILE = 9

# Snow that's too deep to move through.
OBSTACLE_HEIGHT = 6

# Constant used to mark child locations in the map, not used in this player.
GROUND_CHILD = 10

# Representation of a 2D point, used for playing field locations.
class Point:
    def __init__( self, xv, yv ):
        self.x = xv
        self.y = yv

    def set( self, vx, vy ):
        self.x = vx
        self.y = vy


# Simple representation for a child in the game.
class Child:
    def __init__( self ):
        # Location of the child.
        self.pos = Point( 0, 0 )

        # True if  the child is standing.
        self.standing = 1
    
        # Side the child is on.
        self.color = RED
    
        # What's the child holding.
        self.holding = HOLD_EMPTY
    
        # How many more turns this child is dazed.
        self.dazed = 0
        self.dazedPrev = 0

        self.step = 0
        self.stuck = 0
        self.begin = 0
        self.dropSpace = self.pos
        self.stealsnow = 0


# Simple representation for a child's action
class Move:
    # Action the child is making.
    action = "idle"

    # Destiantion of this action (or null, if it doesn't need one) */
    dest = None

# Return the value of x, clamped to the [ a, b ] range.
def clamp( x, a, b ):
    if x < a:
        return a
    if x > b:
        return b
    return x

# Fill in move m to move the child c twoard the given target location, either
# crawling or running.
def moveToward( c, target, m ):
    if c.standing:
        # Run to the destination
        if c.pos.x != target.x:
            if c.pos.y != target.y:
                # Run diagonally.
                m.action = "run"
                m.dest = Point( c.pos.x + clamp( target.x - c.pos.x, -1, 1 ),
                                c.pos.y + clamp( target.y - c.pos.y, -1, 1 ) )
            else:
                # Run left or right
                m.action = "run"
                m.dest = Point( c.pos.x + clamp( target.x - c.pos.x, -2, 2 ), 
                                c.pos.y )
        elif c.pos.y != target.y:
            # Run up or down.
            m.action = "run"
            m.dest = Point( c.pos.x, 
                            c.pos.y + clamp( target.y - c.pos.y, -2, 2 ) )
    else:
        # Crawl to the destination
        if c.pos.x != target.x:
            # crawl left or right
            m.action = "crawl"
            m.dest = Point( c.pos.x + clamp( target.x - c.pos.x, -1, 1 ), 
                            c.pos.y )
        elif c.pos.y != target.y:
            # crawl up or down.
            m.action = "crawl"
            m.dest = Point( c.pos.x, 
                            c.pos.y + clamp( target.y - c.pos.y, -1, 1 ) )

# Source of randomness
rnd = random.Random()

# Current game score for self (red) and opponent (blue).
score = [ 0, 0 ]

# Current snow height in each cell.
height = []

# Contents of each cell.
ground = []

# Allocate the whole field.  Is there a better way to do this?
for i in range( SIZE ):
    height.append( [ 0 ] * SIZE )
    ground.append( [ 0 ] * SIZE )

# List of children on the field, half for each team.
cList = []

# Random destination for each player.
runTarget = []

# How long the child has left to run toward its destination.
runTimer = []
def rounds( x):
    if ( x < 0 ):
      return (round( -x ))

    return (round( x ))

def stuffInWay(c, j, k, destx, desty, ground, cList):
    x2 = j
    y2 = k
    x1 = c.pos.x
    y1 = c.pos.y
    objectInWay = False
    n = max( abs( destx - x1 ), abs( desty - y1 ))
    for t in range(1, n+1):
        x = int(( x1 + rounds( ( t *( destx - x1 ) )/n )))
        y = int(( y1 + rounds( ( t *( desty - y1 ) )/n )))
        currentPos = Point( x, y)
        if x == j and y == k:
            break
        if ground[clamp(currentPos.x,1,SIZE-1)][clamp(currentPos.y,1,SIZE-1)] == GROUND_TREE or ground[clamp(currentPos.x,1,SIZE-1)][clamp(currentPos.y,1,SIZE-1)] == GROUND_SMR:
            objectInWay = True
            break
        for c in range(CCOUNT):
            if currentPos == cList[c].pos:
                objectInWay = True
                break
    return objectInWay

#def closestSnowman (c, m, height, i, ground, runTarget, runTimer):
    
   
def offenseMove(c, m, height,i, ground, runTarget, runTimer):
    adjacentSpaces = []
    nearDist = 1000
    for ox in range( c.pos.x - 1, c.pos.x + 2 ):
        for oy in range( c.pos.y - 1, c.pos.y + 2 ):
            if not((ox == c.pos.x and oy == c.pos.y)):
                if (height[clamp(ox,1, SIZE-1)][clamp(oy,1,SIZE-1)] > 0 and ground[clamp(ox,1,SIZE-1)][clamp(oy,1,SIZE-1)] == GROUND_EMPTY):
                    adjacentSpaces.append(Point(ox,oy))
    for k in range(SIZE):
        for j in range(SIZE):
            if (k != c.pos.x or j != c.pos.y) and (ground[k][j] == GROUND_SMR):
                dx = (c.pos.x - k)
                dy = (c.pos.y - j)
                if (dx * dx + dy*dy) < nearDist:
                    nearDist = dx * dx + dy * dy
    if c.dazed > 0:
        if i != 1:
            c.begin = 1
        c.stealsnow = 0
    elif i == 2 and c.begin == 0:
        if (c.pos.x >= SIZE/2-8 and c.pos.y >= SIZE/2-8):
            if c.step == 0:
                c.step += 1
            elif c.step == 1:
                m.action = "crouch"
                c.step += 1
            elif c.step == 2:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y + 0)
                c.step += 1
            elif c.step == 3:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y + 0)
                c.step += 1
            elif c.step == 4:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y +0)
                c.step += 1
            elif c.step == 5:
                m.action = "crush"
                c.step += 1
            elif c.step == 6:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 7:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 8:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 9:
                m.action = "crush"
                c.step += 1
            elif c.step == 10:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 11:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 12:
                m.action = "crush"
                c.step += 1
            elif c.step == 13:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 14:
                m.action = "stand"
                c.begin = 1
        else:
            runTarget[i].set(SIZE+rnd.randint(0,2), SIZE+rnd.randint(0,2))
            moveToward(c, runTarget[i],m)

    elif i == 0 and c.begin == 0:
        if c.pos.y >= SIZE/2-3:
            if c.step == 0:
                c.step += 1
            elif c.step == 1:
                m.action = "crouch"
                c.step += 1
            elif c.step == 2:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y + 0)
                c.step += 1
            elif c.step == 3:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y + 0)
                c.step += 1
            elif c.step == 4:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y +0)
                c.step += 1
            elif c.step == 5:
                m.action = "crush"
                c.step += 1
            elif c.step == 6:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 7:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 8:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 9:
                m.action = "crush"
                c.step += 1
            elif c.step == 10:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 11:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 12:
                m.action = "crush"
                c.step += 1
            elif c.step == 13:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 14:
                m.action = "stand"
                c.begin = 1
            
            
        else:
            runTarget[i].set(SIZE - 29+rnd.randint(0,2), SIZE+rnd.randint(0,2))
            moveToward(c, runTarget[i],m)

    elif i == 3 and c.begin == 0:
        if c.pos.x > SIZE/2 - 3:
            if c.step == 0:
                c.step += 1
            elif c.step == 1:
                m.action = "crouch"
                c.step += 1
            elif c.step == 2:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y + 0)
                c.step += 1
            elif c.step == 3:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y + 0)
                c.step += 1
            elif c.step == 4:
                m.action = "pickup"
                m.dest = Point(c.pos.x + 1,c.pos.y +0)
                c.step += 1
            elif c.step == 5:
                m.action = "crush"
                c.step += 1
            elif c.step == 6:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 7:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 8:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 9:
                m.action = "crush"
                c.step += 1
            elif c.step == 10:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 11:
                m.action = "pickup"
                m.dest = Point(c.pos.x+1,c.pos.y+1)
                c.step += 1
            elif c.step == 12:
                m.action = "crush"
                c.step += 1
            elif c.step == 13:
                m.action = "drop"
                m.dest = Point(c.pos.x+1,c.pos.y+0)
                c.step += 1
            elif c.step == 14:
                m.action = "stand"
                c.begin = 1


        else:
            runTarget[i].set(SIZE+rnd.randint(0,2), SIZE-29+rnd.randint(0,2))
            moveToward(c, runTarget[i],m)
    elif i == 1 and c.begin == 0:
        defenseBegin(c, m, height,i, ground, runTarget, runTimer, cList)


    
    else:
        if c.dazed == 0 and c.begin >= 1:
        # See if the child needs a new destination.
            while runTimer[ i ] <= 0 or runTarget[ i ] == c.pos:
                runTarget[ i ].set( rnd.randint( SIZE-15, SIZE - 3 ),
                                    rnd.randint( SIZE-15, SIZE - 3 ) )
                runTimer[ i ] = rnd.uniform( 1, 14 )

        # Try to acquire a snowball if we need one.
        if c.holding != HOLD_S1 and c.stealsnow== 0:
            # Crush into a snowball, if we have snow.
            if c.holding == HOLD_P1:
                m.action = "crush"
            else:
                # We don't have snow, see if there is some nearby.

                if c.standing:
                    m.action = "crouch"
                else:
                    Pos = Point(0,0)
                    for ax in range( c.pos.x - 1, c.pos.x + 2 ):
                        for ay in range( c.pos.y - 1, c.pos.y + 2 ):
                            if not((ax == c.pos.x and ay == c.pos.y)):
                                if (height[clamp(ax,1,SIZE-1)][clamp(ay,1,SIZE-1)] > 0 and ground[clamp(ax,1,SIZE-1)][clamp(ay,1,SIZE-1)] == GROUND_EMPTY):
                                    Pos.set(clamp(ax,1,SIZE-1),clamp(ay,1,SIZE-1))
                                    break
                    if Pos != Point(0,0):
                        m.dest = Pos
                        m.action = "pickup"
                    
                    else:
                        m.action = "idle"

        else:
            # Stand up if the child is armed.
            if (not c.standing) and c.stealsnow == 0:
                m.action = "stand"
            else:
                # Try to find a victim.
                victimFound = 0
                j = CCOUNT
                aid = 0
                aidDest = Point(0,0)
                while j < CCOUNT * 2 and not victimFound:
                    if cList[ j ].pos.x >= 0:
                        # We know where this child is, see if it's not too far away.
                        dx = cList[ j ].pos.x - c.pos.x
                        dy = cList[ j ].pos.y - c.pos.y
                        dsq = (dx * dx + dy * dy)**.5
                        if ((dx * 2)**2 + (dy*2)**2)**.5 <= 24 and cList[j].dazed <= 1:
                            victimFound = 1
                            objectInWay = stuffInWay(c, cList[j].pos.x, cList[j].pos.y,c.pos.x+dx*2, c.pos.y + dy*2, ground, cList)
                            if objectInWay == False and c.holding == HOLD_S1:
                                m.action = "throw"
                                # throw past the victim, so we will probably hit them
                                # before the snowball falls into the snow.
                                m.dest = Point( c.pos.x + dx * 2,
                                                c.pos.y + dy * 2 )
                                c.step = 0

                    j += 1
                for d in range(CCOUNT):
                    if cList[d] != c and cList[d].dazed > 0:
                        aid = 1
                        aidDest.set(cList[d].pos.x + rnd.randint(-3,3), cList[d].pos.y + rnd.randint(-3,3))
                        break

                if c.stealsnow == 0:
                    snowmen = []
                    for bx in range( clamp(c.pos.x - 7, 1, SIZE), clamp(c.pos.x + 7, 1, SIZE) ):
                        for by in range(clamp( c.pos.y - 7, 1, SIZE), clamp(c.pos.y + 7, 1, SIZE )):
                            if (ground[bx][by] == 9 or ground[bx][by] == 6):
                                snowmen.append(Point(bx,by))
                    if len(snowmen) > 0:
                        closest = snowmen[0]
                        for snowman in snowmen:
                            if ((snowman.x - c.pos.x)**2 + (snowman.y - c.pos.y)**2)**.5 < ((closest.x - c.pos.x)**2 + (snowman.y - c.pos.y)**2)**.5:
                                closest = snowman
                        c.dropSpace = closest
                        for dx in range( c.pos.x - 1, c.pos.x + 2 ):
                            for dy in range( c.pos.y - 1, c.pos.y + 2 ):
                                if dy == c.dropSpace.y and dx == c.dropSpace.x and not (c.dropSpace.y == c.pos.y and c.dropSpace.y == c.pos.x):
                                    c.stealsnow = 1
                                    break
                                else:
                                    moveToward(c, Point(c.dropSpace.x+rnd.randint(-1,1), c.dropSpace.y+rnd.randint(-1,1)) , m)
                                    break
                elif c.stealsnow == 1 and height[c.dropSpace.x][c.dropSpace.y] < 9:
                    m.dest = c.dropSpace
                    m.action = "drop"
                    c.stealsnow = 0
##                elif c.stealsnow == 1:
##                    n = Point(0,0)
##                    for ox in range( c.pos.x - 1, c.pos.x + 2 ):
##                        for oy in range( c.pos.y - 1, c.pos.y + 2 ):
##                            if not((ox == c.pos.x and oy == c.pos.y) or (ox == c.dropSpace.x and oy == c.dropSpace.y)):
##                                n.set(ox,oy)
##                                
##                    m.dest = n
##                    c.action = "drop"
##                    c.stealsnow = 2
##                elif c.stealsnow == 2:
##                    c.action = "crouch"
##                    c.stealsnow = 3
##                elif c.stealsnow == 3:
##                    c.action = "pickup"
##                    m.dest = c.dropSpace
##                    c.stealsnow = 1
##
##                elif c.stealsnow == 1 and height[c.dropSpace.x][c.dropSpace.y] == 9:
##                    m.action = "crouch"
##                    c.stealsnow = 2

                    
                elif c.stealsnow == 1:
                    Pos = Point(0,0)
                    for cx in range( c.pos.x - 1, c.pos.x + 2 ):
                        for cy in range( c.pos.y - 1, c.pos.y + 2 ):
                            if not((cx == c.pos.x and cy == c.pos.y)):
                                if (ground[clamp(cx,1,SIZE-1)][clamp(cy,1,SIZE-1)] == GROUND_EMPTY and (clamp(cx,1,SIZE-1) != c.dropSpace.x and clamp(cy,1,SIZE-1) != c.dropSpace.y)):
                                    Pos.set(clamp(cx,1,SIZE-1),clamp(cy,1,SIZE-1))
                                    break
                    if Pos.x != 0 and Pos.y != 0:
                        m.dest = Pos
                        m.action = "drop"
                        c.stealsnow = 2
                    else:
                        c.stealsnow =0
                elif c.stealsnow == 2:
                    if c.standing == 0:
                        m.dest = c.dropSpace
                        m.action = "pickup"
                        c.stealsnow = 3
                    else:
                        m.action = "crouch"
                elif c.stealsnow == 3:
                    m.dest = c.dropSpace
                    m.action = "drop"
                    c.stealsnow = 4
                elif c.stealsnow == 4:
                    m.action = "stand"
                    c.stealsnow = 0
                    
                
                    

                elif aid == 1 and victimFound == 0:
                    moveToward(c, Point(aidDest.x + rnd.randint(-2,2), aidDest.y + rnd.randint(-2,2)), m)
                    aid = 0
            # Try to run toward the destination.
            if m.action == "idle":
                for d in range(CCOUNT, CCOUNT*2):
                    if cList[d].pos.x >= 0:
                        runTarget[i] == cList[d].pos
                        break
                moveToward( c, runTarget[ i ], m )
                runTimer[ i ] -= 1

def defenseBegin(c, m, height,i, ground, runTarget, runTimer, cList):
    nearDist = 1000
    good = 1
    adjacentSpaces = []
    snowHeightTotal = 0
    for ox in range( c.pos.x - 1, c.pos.x + 2 ):
            for oy in range( c.pos.y - 1, c.pos.y + 2 ):
                if not((ox == c.pos.x and oy == c.pos.y)):
                    if (height[clamp(ox, 1, SIZE-1)][clamp(oy,1,SIZE-1)] > 0 and ground[clamp(ox,1,SIZE-1)][clamp(oy,1,SIZE-1)] == GROUND_EMPTY):
                        snowHeightTotal += height[clamp(ox,1,SIZE-1)][clamp(oy,1,SIZE-1)]
                        adjacentSpaces.append(Point(clamp(ox, 1, SIZE-1),clamp(oy, 1, SIZE-1)))
    

                                    
        
    if c.step == 0 :
        if len(adjacentSpaces) > 0:
            c.dropSpace = adjacentSpaces[rnd.randint(0,len(adjacentSpaces)-1)]
        else:
            good = 0
        if nearDist > 4 * 4 and good == 1:
            c.step += 1
            c.stuck = 0
        else:
            runTarget[i].set(rnd.randint(0,SIZE-3), rnd.randint(0,SIZE-3))
            moveToward(c, runTarget[i], m)
            c.stuck +=1
    elif c.step == 1:
        m.action = "crouch"
        c.step += 1
    elif c.step == 2:
        m.action = "pickup"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 3:
        m.action = "pickup"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 4:
        m.action = "pickup"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 5:
        m.action = "crush"
        c.step += 1
    elif c.step == 6:
        m.action = "drop"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 7:
        m.action = "pickup"
        m.dest = adjacentSpaces[rnd.randint(0,len(adjacentSpaces)-1)]
        c.step += 1
    elif c.step == 8:
        m.action = "pickup"
        m.dest = adjacentSpaces[rnd.randint(0,len(adjacentSpaces)-1)]
        c.step += 1
    elif c.step == 9:
        m.action = "crush"
        c.step += 1
    elif c.step == 10:
        m.action = "drop"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 11:
        m.action = "pickup"
        m.dest = adjacentSpaces[rnd.randint(0,len(adjacentSpaces)-1)]
        c.step += 1
    elif c.step == 12:
        m.action = "crush"
        c.step += 1
    elif c.step == 13:
        m.action = "drop"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 14:
        m.action = "stand"
        c.step = 0
        c.begin = 2
def defenseMove(c, m, height,i, ground, runTarget, runTimer, cList):
    nearDist = 1000
    good = 1
    adjacentSpaces = []
    snowHeightTotal = 0
    for k in range(SIZE):
        for j in range(SIZE):
            if (k != c.pos.x or j != c.pos.y) and (ground[k][j] == GROUND_SMR):
                dx = (c.pos.x - k)
                dy = (c.pos.y - j)
                if (dx * dx + dy*dy) < nearDist:
                    nearDist = dx * dx + dy * dy

##    for ox in range( c.pos.x - 1, c.pos.x + 2 ):
##        for oy in range( c.pos.y - 1, c.pos.y + 2 ):
##            # Is there snow to pick up?
##            if (ox != c.pos.x and oy != c.pos.y and ground[ ox ][ oy ] == GROUND_CHILD and height[ ox ][ oy ] > 3 ) :
##                c.step = 0
##                break
    for ox in range( c.pos.x - 1, c.pos.x + 2 ):
            for oy in range( c.pos.y - 1, c.pos.y + 2 ):
                if not((ox == c.pos.x and oy == c.pos.y)):
                    if (height[clamp(ox, 1, SIZE-1)][clamp(oy,1,SIZE-1)] > 0 and ground[clamp(ox,1,SIZE-1)][clamp(oy,1,SIZE-1)] == GROUND_EMPTY):
                        snowHeightTotal += height[clamp(ox,1,SIZE-1)][clamp(oy,1,SIZE-1)]
                        adjacentSpaces.append(Point(clamp(ox, 1, SIZE-1),clamp(oy, 1, SIZE-1)))
    if snowHeightTotal >= 6:
        good = 1
    if len(adjacentSpaces) == 0:
        c.step = 0

    if c.stuck > 10:
        if c.holding == 4 or c.holding == 0:
            c.step = 21
        else:
            c.step = 20
        c.stuck = 0
    if c.dazed > 0:
        c.stealsnow = 0
        c.begin = 2
        if c.holding == 4 or c.holding == 0:
            c.step = 21
        else:
            c.step = 20
    elif c.begin == 0:
        defenseBegin(c, m, height,i, ground, runTarget, runTimer, cList)
    elif c.step == 0:
        
        if nearDist > 5 * 5 and good == 1:
            c.step += 1
            c.stuck = 0
        else:
            runTarget[i].set(rnd.randint(c.pos.x,c.pos.x+5), rnd.randint(c.pos.y,c.pos.y+5))
            moveToward(c, runTarget[i], m)
            c.stuck +=1
    elif c.step == 1:
        m.action = "crouch"
        c.step += 1
    elif c.step == 2:
        m.action = "pickup"
        randomSpace = rnd.randint(0, max(0,len(adjacentSpaces)-1))
        m.dest = adjacentSpaces[randomSpace]
        c.step += 1
    elif c.step == 3:
        m.action = "pickup"
        randomSpace = rnd.randint(0, max(0,len(adjacentSpaces)-1))
        m.dest = adjacentSpaces[randomSpace]
        c.step += 1
    elif c.step == 4:
        m.action = "pickup"
        randomSpace = rnd.randint(0, max(len(adjacentSpaces)-1,0))
        m.dest = adjacentSpaces[randomSpace]
        c.step += 1
    elif c.step == 5:
        m.action = "crush"
        c.step += 1
    elif c.step == 6:
        m.action = "drop"
        for space in adjacentSpaces:
            if height[space.x][space.y] <= 3:
                c.dropSpace = space
                break
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 7:
        randomSpace = rnd.randint(0, max(0,len(adjacentSpaces)-1))
        m.dest = adjacentSpaces[randomSpace]
        m.action = "pickup"
        c.step += 1
    elif c.step == 8:
        m.action = "pickup"
        randomSpace = rnd.randint(0, max(0,len(adjacentSpaces)-1))
        m.dest = adjacentSpaces[randomSpace]
        c.step += 1
    elif c.step == 9:
        m.action = "crush"
        c.step += 1
    elif c.step == 10:
        m.action = "drop"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 11:
        m.action = "pickup"
        randomSpace = rnd.randint(0, max(0,len(adjacentSpaces)-1))
        m.dest = adjacentSpaces[randomSpace]
        c.step += 1
    elif c.step == 12:
        m.action = "crush"
        c.step += 1
    elif c.step == 13:
        m.action = "drop"
        m.dest = c.dropSpace
        c.step += 1
    elif c.step == 14:
        m.action = "stand"
        c.step = 0
    elif c.step == 20:
        m.action = "drop"
        m.dest = Point(c.pos.x+1, c.pos.y+0)
        c.step = 21
    elif c.step == 21:
        c.begin = 2
        offenseMove(c, m, height,i, ground, runTarget, runTimer)


    elif c.stealsnow == 0 and c.step == 0:
        snowmen = []
        for bx in range( clamp(c.pos.x - 7, 1, SIZE), clamp(c.pos.x + 7, 1, SIZE) ):
            for by in range(clamp( c.pos.y - 7, 1, SIZE), clamp(c.pos.y + 7, 1, SIZE )):
                if (ground[bx][by] == 9 or ground[bx][by] == 6):
                    snowmen.append(Point(bx,by))
        if len(snowmen) > 0:
            closest = snowmen[0]
            for snowman in snowmen:
                if ((snowman.x - c.pos.x)**2 + (snowman.y - c.pos.y)**2)**.5 < ((closest.x - c.pos.x)**2 + (snowman.y - c.pos.y)**2)**.5:
                    closest = snowman
            c.dropSpace = closest
            for dx in range( c.pos.x - 1, c.pos.x + 2 ):
                for dy in range( c.pos.y - 1, c.pos.y + 2 ):
                    if dy == c.dropSpace.y and dx == c.dropSpace.x and not (c.dropSpace.y == c.pos.y and c.dropSpace.y == c.pos.x):
                        c.stealsnow = 1
                        break
                    else:
                        moveToward(c, Point(c.dropSpace.x+rnd.randint(-1,1), c.dropSpace.y+rnd.randint(-1,1)) , m)
                        break
    elif c.stealsnow == 1 and height[c.dropSpace.x][c.dropSpace.y] < 9:
        m.dest = c.dropSpace
        m.action = "drop"
        c.stealsnow = 0


        
    elif c.stealsnow == 1:
        Pos = Point(0,0)
        for cx in range( c.pos.x - 1, c.pos.x + 2 ):
            for cy in range( c.pos.y - 1, c.pos.y + 2 ):
                if not((cx == c.pos.x and cy == c.pos.y)):
                    if (ground[clamp(cx,1,SIZE-1)][clamp(cy,1,SIZE-1)] == GROUND_EMPTY and (clamp(cx,1,SIZE-1) != c.dropSpace.x and clamp(cy,1,SIZE-1) != c.dropSpace.y)):
                        Pos.set(clamp(cx,1,SIZE-1),clamp(cy,1,SIZE-1))
                        break
        if Pos.x != 0 and Pos.y != 0:
            m.dest = Pos
            m.action = "drop"
            c.stealsnow = 2
        else:
            c.stealsnow =0
    elif c.stealsnow == 2:
        if c.standing == 0:
            m.dest = c.dropSpace
            m.action = "pickup"
            c.stealsnow = 3
        else:
            m.action = "crouch"
    elif c.stealsnow == 3:
        m.dest = c.dropSpace
        m.action = "drop"
        c.stealsnow = 4
    elif c.stealsnow == 4:
        m.action = "stand"
        c.stealsnow = 0


    

for i in range( 2 * CCOUNT ):
    cList.append( Child() )
    runTarget.append( Point( 0, 0 ) )
    runTimer.append( 0 )

turnNum = string.atoi( sys.stdin.readline() )
while turnNum >= 0:
    # read the scores of the two sides.
    tokens = string.split( sys.stdin.readline() )
    score[ RED ] = tokens[ 0 ]
    score[ BLUE ] = tokens[ 1 ]
    
    # Parse the current map.
    for i in range( SIZE ):
        tokens = string.split( sys.stdin.readline() )
        for j in range( SIZE ):
            # Can we see this cell?
            if tokens[ j ][ 0 ] == '*':
                height[ i ][ j ] = -1
                ground[ i ][ j ] = -1
            else:
                height[ i ][ j ] = string.find( string.digits, tokens[ j ][ 0 ] )
                ground[ i ][ j ] = string.find( string.ascii_lowercase, tokens[ j ][ 1 ] )
                
    # Read the states of all the children.
    for i in range( CCOUNT * 2 ):
        c = cList[ i ]
        
        # Can we see this child?        
        tokens = string.split( sys.stdin.readline() )
        if tokens[ 0 ] == "*":
            c.pos.x = -1
            c.pos.y = -1
        else:
            # Record the child's location.
            c.pos.x = string.atoi( tokens[ 0 ] )
            c.pos.y = string.atoi( tokens[ 1 ] )

            # Compute child color based on it's index.
            if i < CCOUNT:
                c.color = RED
            else:
                c.color = BLUE
        
            # Read the stance, what the child is holding and how much
            # longer he's dazed.
            c.standing = ( tokens[ 2 ] == "S" )
            
            c.holding = string.find( string.ascii_lowercase, tokens[ 3 ] )

            c.dazed = string.atoi( tokens[ 4 ] )

    # Mark all the children in the map, so they are easy to
    # look up.
    for i in range( 2 * CCOUNT ):
        c = cList[ i ]
        if c.pos.x >= 0:
            ground[ c.pos.x ][ c.pos.y ] = GROUND_CHILD
    for i in range( CCOUNT ):
        c = cList[i]
        m = Move()
        if i == 0 or i == 2 or i == 3:
            offenseMove(c, m, height, i, ground, runTarget, runTimer)
        else:
            defenseMove(c, m, height,i, ground, runTarget, runTimer, cList)
        if m.dest == None:
            sys.stdout.write( "%s\n" % m.action )
        else:
            sys.stdout.write( "%s %d %d\n" % ( m.action, m.dest.x, m.dest.y ) )
    sys.stdout.flush()
    turnNum = string.atoi( sys.stdin.readline() )
