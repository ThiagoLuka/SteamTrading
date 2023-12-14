from data_models.query.SteamBadgesRepository import SteamBadgesRepository
from utils.MathUtils import MathUtils


class SteamBadges:

    def __init__(self):
        # it won't have a state for now because the only functionality implemented is quite simple
        # it might have spin off another class more related to badges per se, not badges that a user have
        pass

    @staticmethod
    def get_user_level(user_id: int) -> int:
        # Steam levels are earned by raising experience. The first 10 levels are earned with 100xp each
        # From level 10-20 one needs 200xp for each, between 20-30 300xp each, and so it goes on
        # Following this rule and using a little math, one could know the steam level given a certain experience
        # by figuring out that the level could be split into the tens, which follow a triangular sequence times 1000,
        # and the units, which follow a linear progression of the nth element of the triangular sequence time 100
        # That's why this weird calculation that comes after works
        user_xp: int = SteamBadgesRepository.get_user_total_experience(user_id)
        thousand_xp_to_this_ten, level_tens = MathUtils.highest_triangular_number_and_nth_term_below(user_xp // 1000)
        user_xp_units = user_xp - (thousand_xp_to_this_ten * 1000)
        level_units = user_xp_units // ((level_tens + 1) * 100)
        level = 10 * level_tens + level_units
        return level
