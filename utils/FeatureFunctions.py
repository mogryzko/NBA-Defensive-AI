import math
import random

# frame is a moment in time, or a list of 11 lists that contain player and ball information
class Frame:
    # order of the calls in the __init__ function is important
    def __init__(self, frame, player_in_question_id, player_in_question_team_id, ball_handler=None,prev_frame=None):
        self.frame = frame
        self.prev_frame = (prev_frame.frame if prev_frame != None else frame)
        self.ball_moment = self.frame[0]
        self.player_moments = self.frame[1:]
        self.player_in_question_id = player_in_question_id
        self.player_in_question_team_id = player_in_question_team_id
        self.frame_order = self.sortByPlayerNearestBall()
        self.sortPrevFrame()
        self.ball_handler = (ball_handler if ball_handler!=None else self.player_moments[0][1])
        self.velocities = self.getVelocities()
        self.dxdys = self.getDxDy()
        self.distances_from_hoop, self.hoop = self.getDistancesFromHoop()
        self.iso_tag = self.isIsoFrame()
        self.addAttributes()

    def __str__(self):
        return str(self.frame)

    # adds current velocity, direction of movement(dx, dy), distance from closest hoop to frame
    def addAttributes(self):
        velocities = self.velocities
        dxdys = self.dxdys
        distances_from_hoop = self.distances_from_hoop
        for i in range(0, len(self.frame)):
            self.frame[i].extend((velocities[i], dxdys[i][0], dxdys[i][1], distances_from_hoop[i]))

    # returns an array with the velocities of each player or ball in the frame
    def getVelocities(self):
        velocities = []
        for player_or_ball_curr,player_or_ball_prev in zip(self.frame, self.prev_frame):
            if self.frame != self.prev_frame:
                velocity = float('%.3f'%(1000*self.findDistance(player_or_ball_curr, player_or_ball_prev)/
                                                 (player_or_ball_curr[5] - player_or_ball_prev[5])))
            else:
                velocity = 0
            velocities.append(velocity)
        return velocities

    # returns an array with the change of x an y position for each player or ball in the frame as a tuple
    def getDxDy(self):
        dxdy = []
        for player_or_ball_curr,player_or_ball_prev in zip(self.frame, self.prev_frame):
            dx = float('%.5f'%(player_or_ball_curr[2] - player_or_ball_prev[2]))
            dy = float('%.5f'%(player_or_ball_curr[3] - player_or_ball_prev[3]))
            dxdy.append((dx,dy))
        return dxdy

    # returns list of player and ball distances from closest hoop to ball at current frame, as well as coordinates for closest hoop
    def getDistancesFromHoop(self):
        distances = []
        distance_to_right = self.findDistanceXY(self.ball_moment[2], 89, self.ball_moment[3], 25)
        distance_to_left = self.findDistanceXY(self.ball_moment[2], 5, self.ball_moment[3], 25)
        if distance_to_left >= distance_to_right:
            hoop = (89,25)
        else:
            hoop = (5,25)
        for player_or_ball in self.frame:
            distance_to_hoop = self.findDistanceXY(player_or_ball[2],hoop[0],player_or_ball[3],hoop[1])
            distance_to_hoop = float('%.3f' % distance_to_hoop)
            distances.append(distance_to_hoop)
        return distances, hoop


    # returns whether the current frame is a moment in time where the player in question is playing iso defense
    # (offensive player has ball and player in question is closest defender to them)
    def isIsoFrame(self):
        # sanity check: the ball is in the play
        if not self.frame[0][0] == -1: return False
        # if the ball is not in the possession of any player, then it is not an iso defensive situation
        if self.findDistance(self.player_moments[0], self.ball_moment) > 4: return False
        # if the player in possession of the ball is on the same team as the player in question, then not a defensive possession
        if self.player_moments[0][0] == self.player_in_question_team_id: return False
        # if the ball is further than 35 ft from either basket, then it is most likely a transition play
        if 35 < self.ball_moment[2] < 59: return False
        # if a subset of 4 random players are all moving in the same direction, then it is most likely a transition play
        rand_nums = random.sample(range(1, 10), 4)
        move_dir = []
        for num in rand_nums:
            x = self.dxdys[num]
            move_dir.append(x[0] > 0)
        if all(move_dir) or not any(move_dir): return False

        # finally, if the frame passes the previous cases, and player in question is the second closest
        # player to the ball (within 15 ft), then it is the case we are looking for
        if self.player_moments[1][1] == self.player_in_question_id and self.findDistance(self.player_moments[1], self.ball_moment) < 15:
            return True
        # else not an iso defensive frame
        return False

    # sorts players in frame by their distance to the ball, returns order of players in sorted list
    def sortByPlayerNearestBall(self):
        frame_order = []
        self.player_moments.sort(key=lambda x: math.sqrt((x[2] - self.ball_moment[2]) ** 2 + (x[3] - self.ball_moment[3]) ** 2))
        self.frame = []
        self.frame.append(self.ball_moment)
        frame_order.append(-1)
        for x in range(0, len(self.player_moments)):
            self.frame.append(self.player_moments[x])
            frame_order.append(self.player_moments[x][1])
        return frame_order

    # sorts players in prev_frame to be in the same order as frame
    # error occurs when dataset has incorrect player numbers, when this is the case, we just sort prev_frame by which
    # player is closest to the ball, to be similar enough to frame
    def sortPrevFrame(self):
        try:
            self.prev_frame.sort(key=lambda x: self.frame_order.index(x[1]))
        except ValueError:
            prev_player_moments = self.prev_frame[1:]
            prev_player_moments.sort(
                key=lambda x: math.sqrt((x[2] - self.prev_frame[0][2]) ** 2 + (x[3] - self.prev_frame[0][3]) ** 2))
            self.prev_frame = [self.prev_frame[0]] + prev_player_moments

    def findDistanceXY(self,x1,x2,y1,y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def findDistance(self, player_moment1, player_moment2):
        return math.sqrt((player_moment1[2] - player_moment2[2]) ** 2 + (player_moment1[3] - player_moment2[3]) ** 2)

    # returns whether player in question is in the current play
    def playerInFrame(self, playerid):
        for player_moment in self.player_moments:
            if player_moment[1] == playerid: return True
        return False



class IsoMoment:
    def __init__(self, player_in_question_id, ball_handler_id):
        self.frames = []
        self.player_in_question_id = player_in_question_id
        self.ball_handler_id = ball_handler_id
    def __len__(self):
        return len(self.frames)

    def __str__(self):
        to_print = [frame.frame for frame in self.frames]
        return str(to_print)

    def addFrame(self, frame):
        self.frames.append(frame)
        if not self.ball_handler_id: self.ball_handler_id = frame.frame[1][1]

    def removeFrame(self, num_frames_to_remove):
        self.frames = self.frames[:-num_frames_to_remove]
        #self.data = self.data[:-num_frames_to_remove * 11]

    # there is a lot of data in each frame that we don't need. Features will contain:
    # (x position, y position, velocity, dx, dy, distance from hoop) for both player in question and ball handler,
    # then next x and y position for piq (as our gold key values)
    # also note that all x and y positions are moved to one side of the court
    def convertFramesToFeatureVectors(self):
        feature_vectors = []
        for i in range(len(self.frames) - 1):
            player_in_question = []
            ball_handler = []
            player_in_question_gold = []
            for j in range(1,len(self.frames[i].frame)):
                if self.frames[i].frame[j][1] == self.player_in_question_id:
                    player_in_question = self.toHalfcourt(self.frames[i].frame[j])
                if self.frames[i].frame[j][1] == self.ball_handler_id:
                    ball_handler = self.toHalfcourt(self.frames[i].frame[j])
                if self.frames[i+1].frame[j][1] == self.player_in_question_id:
                    player_in_question_gold = self.toHalfcourt(self.frames[i+1].frame[j])
                if player_in_question_gold and player_in_question and ball_handler: break
            current_vector = [player_in_question[x] for x in [2,3,10,11,12,13]] \
                             + [ball_handler[x] for x in [2,3,10,11,12,13]] \
                             + [player_in_question_gold[x] for x in [2,3]]
            feature_vectors.append(current_vector)
        return feature_vectors

    def toHalfcourt(self, moment):
        if moment[2] > 47:
            moment[2] = float('%.5f' % (94 - moment[2]))
            moment[11] = -1 * moment[11]
        return moment


class Event:
    def __init__(self, event, player_in_question_id, player_in_question_team_id):
        self.event = event
        self.player_in_question_id = player_in_question_id
        self.player_in_question_team_id = player_in_question_team_id
        self.event_id = self.event["eventId"]
        self.home_team_id = self.event["home"]["teamid"]
        self.away_team_id = self.event["visitor"]["teamid"]
        self.movement_data = event["moments"]
        self.players_in_event = self.getPlayersInEvent()

    # returns playerids of every player in the current event
    def getPlayersInEvent(self):
        player_ids = []
        for player_or_ball_moment in self.movement_data[0][5]:
            player_ids.append(player_or_ball_moment[1])
        return player_ids

    def playerInPlay(self, player_id):
        return True if player_id in self.getPlayersInEvent() else False

    def findIsoMoments(self):
        moments = []
        iso_trigger = False
        iso_moment_num = 1
        not_iso_counter = 0
        current_iso_moment = IsoMoment(self.player_in_question_id, None)
        current_frame = None
        prev_frame = None
        ball_handler = None # opponent handling ball
        for moment in self.movement_data:
            if len(moment[5]) != 11: continue #work around messes in dataset
            for player_or_ball in moment[5]:
                player_or_ball.extend((moment[1], moment[2], moment[3], self.event_id, iso_moment_num))
            prev_frame = current_frame
            current_frame = Frame(moment[5], self.player_in_question_id, self.player_in_question_team_id, ball_handler, prev_frame)
            if not iso_trigger and current_frame.iso_tag:
                ball_handler = current_frame.player_moments[0][1]
            if current_frame.iso_tag:
                iso_trigger = True
                not_iso_counter = 0
            if iso_trigger and not current_frame.iso_tag:
                not_iso_counter += 1
            if iso_trigger and not_iso_counter == 10:
                iso_trigger = False
                not_iso_counter = 0
                current_iso_moment.removeFrame(10)
                ball_handler = None
            if iso_trigger:
                current_iso_moment.addFrame(current_frame)
            if not iso_trigger and len(current_iso_moment) > 35:
                moments.append(current_iso_moment)
                iso_moment_num += 1
                current_iso_moment = IsoMoment(self.player_in_question_id, ball_handler)
            elif not iso_trigger and len(current_iso_moment) <= 35:
                current_iso_moment = IsoMoment(self.player_in_question_id, ball_handler)
        return moments
