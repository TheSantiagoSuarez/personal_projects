import FIX_fpl_methods as methods

class FPLmanager:
    def __init__(self, ID, id2, name, lastname, short_name, team_name):
        self.ID = ID
        self.id2 = id2
        self.name = name
        self.lastname = lastname
        self.short_name = short_name
        self.team_name = team_name
    
    def get_squad_formation(self, picks):
        formation = [0,0,0,0]

        for i in range(1,11):
            key = "pos " + str(i)
            pos = picks.get(key).position
            
            formation[pos-1] = formation[pos-1] + 1

        return formation[1:]

    def get_picks(self, current_gw, players):    
        picks = {}
        for gw in range(1,current_gw+1):
            gw_picks = {}
            raw_picks = methods.get_data(f"https://draft.premierleague.com/api/entry/{self.ID}/event/{gw}").get("picks")
            for pick in raw_picks:
                gw_picks["pos " + str(pick.get("position"))] = methods.get_player(pick.get("element"),players)
            gw_picks["formation"] = self.get_squad_formation(gw_picks)
            picks[gw] = gw_picks
        self.picks = picks

    def get_fixtures(self, matches, managers):
        all_matches = {}
        for match in matches:
            pts_1 = match.player_1_points
            pts_2 = match.player_2_points
            print("match_id: "+str(match.player_1))
            print("self_id: "+str(self.ID))
            print(match.player_1 == self.ID)
            if match.player_1 == self.id2:
                result = "W" if pts_1>pts_2 else "L" if pts_1<pts_2 else "D"
                this_match = {"result":result,"points":pts_1, "opponent":methods.get_manager(match.player_2,managers, "id2"), "opponent_points":pts_2}
                all_matches[match.gw] = this_match
            elif match.player_2 == self.id2:
                result = "L" if pts_1>pts_2 else "W" if pts_1<pts_2 else "D"
                this_match = {"result":result,"points":pts_2, "opponent":methods.get_manager(match.player_1,managers, "id2"), "opponent_points":pts_1}
                all_matches[match.gw] = this_match

        self.fixtures = all_matches

    def get_standings(self, standings_raw, current_gw):
        standings = {}
        
        points = {}
        points["total"] = methods.get_picks_points(self, "total")
        points["gk"] = methods.get_picks_points(self, 1)
        points["def"] = methods.get_picks_points(self, 2)
        points["mid"] = methods.get_picks_points(self, 3)
        points["fwd"] = methods.get_picks_points(self, 4)

        points["bench"] = methods.get_picks_points(self, "bench")
        points["missed"] = methods.get_missed_points(self, current_gw)

        for s in standings_raw:
            if (s["league_entry"] == self.ID) | (s["league_entry"] == self.id2):
                points["points_against"] = s["points_against"]
                points["points_difference"] = sum(points["total"].values()) - points["points_against"]

                standings["points"] = points
                standings["wins"] = s["matches_won"]
                standings["draws"] = s["matches_drawn"]
                standings["losses"] = s["matches_lost"]
                standings["draft_points"] = (standings["wins"]*3) + (standings["draws"])

                print("Standings saved")
                self.standings = standings

    def get_transfers(self, transfers):
        manager_transfers = []
        for transfer in transfers:
            if transfer.manager == self:
                manager_transfers.append(transfer)
        self.transfers = manager_transfers

class FPLplayer:
    def __init__(self, ID, name, team_id, position, photo):
        self.ID = ID
        self.name = name
        self.team_id = team_id                                  
        self.position = position
        self.photo = photo
        self.stats = {}

    def assign_team(self, teams):
        team = next((team for team in teams if team.ID == self.team_id), None)    #Assign team that equals the ID
        self.team = team


class FPLteam:
    def __init__(self, ID, name, badge):
        self.ID = ID
        self.name = name
        self.badge = badge


class Match:
    def __init__(self, dict):
        self.gw = dict["event"]
        self.player_1 = dict["league_entry_1"]
        self.player_1_points = dict["league_entry_1_points"]
        self.player_2 = dict["league_entry_2"]
        self.player_2_points = dict["league_entry_2_points"]


class Transfer:
    def __init__(self, dict, players, managers):
        self.ID = dict["id"]
        self.type = dict["kind"]
        self.result = dict["result"]

        self.player_in = methods.get_player(dict["element_in"],players)
        self.player_out = methods.get_player(dict["element_in"],players)
        self.manager = methods.get_manager(dict["entry"], managers)
        self.gameweek = dict["event"]

class Ranking:
    def __init__(self, first, second, third, last, value, table):
        self.first = first
        self.second = second
        self.third = third
        self.last = last

        self.value = value
        self.table = table