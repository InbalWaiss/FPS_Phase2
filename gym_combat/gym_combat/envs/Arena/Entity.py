
from gym_combat.gym_combat.envs.Arena.AbsDecisionMaker import AbsDecisionMaker
from gym_combat.gym_combat.envs.Common.constants import np, SIZE_H, SIZE_W, DSM, AgentAction, NUMBER_OF_ACTIONS, FIRE_RANGE, BB_MARGIN, ACTION_SPACE_7

possible_azimuth = [i for i in range(0,360,45)] # = [0,45,90,135,180,225,270,315]

class CPoint:

    def __init__(self, h, w):

        self.h = h
        self.w = w

class Entity:
    def __init__(self, decision_maker: AbsDecisionMaker = None):

        self._decision_maker = decision_maker #not in use due to training with stable_baselines3

        self.azimuth = 0
        self.head = CPoint(-1, -1)
        self.tail = CPoint(-1, -1)


    def _get_tail(self, head: CPoint, azimuth):
        tail = CPoint(-1,-1)
        if azimuth==0:
            tail.h = head.h + 1
            tail.w = head.w
        elif azimuth==45:
            tail.h = head.h + 1
            tail.w = head.w - 1
        elif azimuth==90:
            tail.h = head.h
            tail.w = head.w - 1
        elif azimuth == 135:
            tail.h = head.h - 1
            tail.w = head.w - 1
        elif azimuth == 180:
            tail.h = head.h - 1
            tail.w = head.w
        elif azimuth == 225:
            tail.h = head.h - 1
            tail.w = head.w + 1
        elif azimuth==270:
            tail.h = head.h
            tail.w = head.w + 1
        elif azimuth == 315:
            tail.h = head.h + 1
            tail.w = head.w + 1
        else:
            print("illegal azimuth!")
        return tail

    def set_tail(self):
        tail = self._get_tail(self.head, self.azimuth)
        self.tail.h = tail.h
        self.tail.w = tail.w

    def _choose_random_position(self):
        is_obs = True
        while is_obs:
            self.head.h = np.random.randint(0, SIZE_H)
            self.head.w = np.random.randint(0, SIZE_W)
            self.azimuth = np.random.randint(0, len(possible_azimuth))

            is_obs = self.is_obs(self.head, self.azimuth)


    def __str__(self):
        # for debugging purposes
        return f"{self.h}, {self.w}"

    def __sub__(self, other):
        return (self.h - other.h, self.w - other.w)

    def __add__(self, other):
        return (self.h + other.h, self.w + other.w)

    def get_coordinates(self):
        return self.head.h, self.head.w

    def set_coordinatess(self, h, w, azinumth = None):
        self.h = h
        self.w = w
        if azinumth is not None:
            self.azimuth = azinumth
        self.set_tail()

    def check_if_move_is_legal(self, head: CPoint, azimuth):
        is_obs = self.is_obs(head, azimuth)
        return not (is_obs), head.h, head.w, azimuth


    def is_obs(self,head: CPoint, azimuth):
        # if first draw of start point
        if head.h == -1 and head.w == -1:
            return True

        # if head not in bounds return True
        if head.h < 0 or head.w < 0 or head.h >= SIZE_H or head.w >= SIZE_W:
            return True

        # check if head == obs
        if DSM[head.h,head.w] == 1:
            return True

        # else: check if DSM[tail= is legal and free
        tail = self._get_tail(head, azimuth)
        if tail.h <0 or tail.w <0 or tail.h>=SIZE_H or tail.w>=SIZE_W:
            return True
        if DSM[tail.h,tail.w] == 1:
            return True

        # else: in map and not obs!
        return False

    def move_9_actions(self, h=None, w=None):
        # if no value for h- move randomly
        if h==None:
            new_h = self.h + np.random.randint(-1, 2)
        else:
            new_h = self.h + h

        # if no value for w- move randomly
        if w==None:
            new_w = self.w + np.random.randint(-1, 2)
        else:
            new_w = self.w + w

        is_legal, new_h, new_w = self.check_if_move_is_legal(new_h, new_w)
        if is_legal:
            self.head.h = new_h
            self.head.w = new_w
            self.set_tail()
        # else: stay at last spot

    def move(self, h=None, w=None, azimuth=None):
        # if no value for h- move randomly
        if h==None:
            new_h = self.head.h + np.random.randint(-1, 2)
        else:
            new_h = self.head.h + h

        # if no value for w- move randomly
        if w==None:
            new_w = self.head.w + np.random.randint(-1, 2)
        else:
            new_w = self.head.w + w

        if azimuth==None:
            new_azimuth = np.random.randint(0, len(possible_azimuth))
        else:
            new_azimuth = azimuth


        is_legal, new_h, new_w, new_azimuth = self.check_if_move_is_legal(head=CPoint(h=new_h, w=new_w), azimuth=new_azimuth)
        if is_legal:
            self.head.h = new_h
            self.head.w = new_w
            self.azimuth = new_azimuth
            self.set_tail()
        # else: stay at last spot


    def action(self, a: AgentAction):
        if NUMBER_OF_ACTIONS==9:
            """9 possible moves!"""
            # BUG: there is a coordinate switch. Here we changed xs and ys places to fix it.
            if a == AgentAction.TopRight: #1
                self.move_9_actions(h=-1, w=1)
            elif a == AgentAction.Right: #2
                self.move_9_actions(h=0, w=1)
            elif a == AgentAction.BottomRight: #3
                self.move_9_actions(h=1, w=1)
            elif a == AgentAction.Top: # 4
                self.move_9_actions(h=-1, w=0)
            elif a == AgentAction.Stay:  # 5 - stay in place!
                self.move_9_actions(h=0, w=0)
            elif a == AgentAction.Bottom: # 6
                self.move_9_actions(h=1, w=0)
            elif a == AgentAction.TopLeft : # 7
                self.move_9_actions(h=-1, w=-1)
            elif a==AgentAction.Left: #8
                self.move_9_actions(h=0, w=-1)
            elif a == AgentAction.BottomLeft: #0
                self.move_9_actions(h=1, w=-1)

        else: #ACTION_SPACE_7
            """7 possible moves!"""
            azimuth = self.azimuth
            if a == AgentAction.Stay:  # 0
                self.move(h=0, w=0, azimuth=self.azimuth)
            if a == AgentAction.rotate_45_right:  # 1
                azimuth = (azimuth+45)%360
                self.move(h=0, w=0, azimuth=azimuth)
            if a == AgentAction.rotate_90_right:  # 2
                azimuth = (azimuth+90)%360
                self.move(h=0, w=0, azimuth=azimuth)
            if a == AgentAction.rotate_45_left:  # 3
                azimuth = (azimuth-45)%360
                self.move(h=0, w=0, azimuth=azimuth)
            if a == AgentAction.rotate_90_left:  # 4
                azimuth = (azimuth-90)%360
                self.move(h=0, w=0, azimuth=azimuth)
            if a == AgentAction.rotate_180:  # 5
                azimuth = (azimuth+180)%360
                self.move(h=0, w=0, azimuth=azimuth)
            if a == AgentAction.forward:  # 5
                azimuth = self.azimuth
                if azimuth==0:
                    self.move(h=-1, w=0, azimuth=azimuth)
                elif azimuth == 45:
                    self.move(h=-1, w=1, azimuth=azimuth)
                elif azimuth == 90:
                    self.move(h=0, w=+1, azimuth=azimuth)
                elif azimuth == 135:
                    self.move(h=1, w=1, azimuth=azimuth)
                elif azimuth==180:
                    self.move(h=1, w=0, azimuth=azimuth)
                elif azimuth == 225:
                    self.move(h=1, w=-1, azimuth=azimuth)
                elif azimuth == 270:
                    self.move(h=0, w=-1, azimuth=azimuth)
                elif azimuth == 315:
                    self.move(h=-1, w=-1, azimuth=azimuth)




if __name__ == '__main__':
    DSM = np.array([
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 1., 1., 0., 0., 0., 1., 0., 0., 0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 1., 1., 1., 0., 0., 0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 1., 1., 1., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.],
        [0., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
    ])

    entity = Entity()
    entity.head.h = 9
    entity.head.w = 1
    entity.azimuth = 0 # possible_azimuth = [0,45,90,135,180,225,270,315]
    entity.set_tail()

    import matplotlib.pyplot as plt
    import copy

    fig, axs = plt.subplots(2, 2)
    DSM_before = copy.deepcopy(DSM)

    DSM_before[entity.head.h, entity.head.w]= 10
    DSM_before[entity.tail.h, entity.tail.w] = 15
    axs[0, 0].matshow(DSM_before)

    DSM_after = copy.deepcopy(DSM)
    entity.action(AgentAction.rotate_180)
    DSM_after[entity.head.h, entity.head.w]= 10
    DSM_after[entity.tail.h, entity.tail.w] = 15
    axs[0, 1].matshow(DSM_after)

    # plt.matshow(DSM)
    plt.show()

