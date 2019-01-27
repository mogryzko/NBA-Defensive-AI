import os
import sys
sys.path.append('/Users/mogryzko/PycharmProjects/NBA-Defensive-AI/')
# ^Replace with path to your directory
import fnmatch
import json
import pandas as pd
import utils.FeatureFunctions as ff

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("player_w_underscore")
parser.add_argument("team")
args = parser.parse_args()



teamids = {'MIL': 1610612749, 'GSW': 1610612744, 'MIN': 1610612750, 'MIA': 1610612748, 'ATL': 1610612737,
           'BOS': 1610612738, 'DET': 1610612765, 'NYK': 1610612752, 'DEN': 1610612743, 'DAL': 1610612742,
           'BKN': 1610612751, 'POR': 1610612757, 'OKC': 1610612760, 'TOR': 1610612761, 'CLE': 1610612739,
           'SAS': 1610612759, 'CHA': 1610612766, 'UTA': 1610612762, 'CHI': 1610612741, 'HOU': 1610612745,
           'WAS': 1610612764, 'LAL': 1610612747, 'PHI': 1610612755, 'MEM': 1610612763, 'LAC': 1610612746,
           'SAC': 1610612758, 'ORL': 1610612753, 'PHX': 1610612756, 'IND': 1610612754, 'NOP': 1610612740}
playerids = {'Pau Gasol': 2200, 'Tibor Pleiss': 202353, 'George Hill': 201588, 'Joakim Noah': 201149,
              'Derrick Williams': 202682, 'Randy Foye': 200751, 'Mike Miller': 2034, 'Draymond Green': 203110,
              'Kyle Lowry': 200768, 'Raymond Felton': 101109, 'Thaddeus Young': 201152, 'Kostas Papanikolaou': 203123,
              'Kevin Love': 201567, 'Nikola Vucevic': 202696, 'Aaron Brooks': 201166, 'Isaiah Thomas': 202738,
              'Jared Sullinger': 203096, 'Paul Millsap': 200794, 'Avery Bradley': 202340, 'Joe Johnson': 2207,
              'Will Barton': 203115, 'Nik Stauskas': 203917, 'Jerami Grant': 203924, 'James Jones': 2592,
              'DeMarcus Cousins': 202326, 'Michael Carter-Williams': 203487, 'Caron Butler': 2406,
              'Julius Randle': 203944, 'Marc Gasol': 201188, 'Tony Parker': 2225, 'Richaun Holmes': 1626158,
              'LeBron James': 2544, 'Brook Lopez': 201572, 'Dwight Powell': 203939, 'Zach Randolph': 2216,
              'Enes Kanter': 202683, 'Ty Lawson': 201951, 'Wesley Matthews': 202083, 'Sergey Karasev': 203508,
              'Elijah Millsap': 202407, 'Bryce Cotton': 203955, 'Mario Chalmers': 201596, 'Sasha Vujacic': 2756,
              'Justise Winslow': 1626159, 'Jerian Grant': 1626170, 'Khris Middleton': 203114, 'TJ Warren': 203933,
              'Al-Farouq Aminu': 202329, 'Al Horford': 201143, 'Lamar Patterson': 203934, "Kyle O'Quinn": 203124,
              'Joel Anthony': 201202, 'James Johnson': 201949, 'Amir Johnson': 101161, 'Jonathon Simmons': 203613,
              'Luis Montero': 1626242, 'Tyler Zeller': 203092, 'Glenn Robinson': 203922, 'Chris Kaman': 2549,
              'Walter Tavares': 204002, 'Ersan Ilyasova': 101141, 'O.J. Mayo': 201564, 'Donatas Motiejunas': 202700,
              'Jason Smith': 201160, 'Brandon Rush': 201575, 'Manu Ginobili': 1938, 'Reggie Jackson': 202704,
              'Delon Wright': 1626153, 'Jimmy Butler': 202710, 'Courtney Lee': 201584, 'Luol Deng': 2736,
              'PJ Hairston': 203798, 'Jordan Hill': 201941, 'Sam Dekker': 1626155, 'Zaza Pachulia': 2585,
              'Josh Smith': 2746, 'Lucas Nogueira': 203512, 'Jamal Crawford': 2037, 'Joe Ingles': 204060,
              'Tyler Johnson': 204020, 'Noah Vonleh': 203943, 'Jon Leuer': 202720, 'Kentavious Caldwell-Pope': 203484,
              'Rajon Rondo': 200765, 'Maurice Harkless': 203090, 'Cameron Bairstow': 203946, 'DeAndre Jordan': 201599,
              'Jordan Adams': 203919, 'Jordan Clarkson': 203903, 'Goran Dragic': 201609, 'Jeff Withey': 203481,
              'Danilo Gallinari': 201568, 'Stephen Curry': 201939, 'Kevin Martin': 2755, 'Chris Copeland': 203142,
              'Andrew Wiggins': 203952, 'Wesley Johnson': 202325, 'Kelly Olynyk': 203482, 'Steven Adams': 203500,
              'David West': 2561, 'Metta World Peace': 1897, 'Willie Reed': 203186, 'Jeremy Evans': 202379,
              'Tyus Jones': 1626145, 'James Young': 203923, 'Gary Neal': 202390, 'Timofey Mozgov': 202389,
              'Rodney Stuckey': 201155, 'Troy Daniels': 203584, 'Beno Udrih': 2757, 'Omri Casspi': 201956,
              'Chris Paul': 101108, 'Marcus Smart': 203935, 'Kemba Walker': 202689, 'John Jenkins': 203098,
              'Trevor Booker': 202344, 'Tyreke Evans': 201936, 'Reggie Bullock': 203493, 'Meyers Leonard': 203086,
              'Mike Conley': 201144, 'Thabo Sefolosha': 200757, 'Marcus Thornton': 201977, 'Jeff Teague': 201952,
              'Larry Nance Jr.': 1626204, 'Kirk Hinrich': 2550, 'Evan Turner': 202323, 'Trevor Ariza': 2772,
              'Cameron Payne': 1626166, 'Cory Joseph': 202709, 'Monta Ellis': 101145, 'Lavoy Allen': 202730,
              'Zach LaVine': 203897, 'Mike Scott': 203118, 'Shelvin Mack': 202714, 'Jeff Green': 201145,
              'Donald Sloan': 202388, 'Gorgui Dieng': 203476, 'Roy Hibbert': 201579, 'TJ McConnell': 204456,
              'Tony Allen': 2754, 'James Harden': 201935, 'Kevin Durant': 201142, 'Chris Johnson': 203187,
              'JaVale McGee': 201580, 'Justin Anderson': 1626147, 'Austin Rivers': 203085, 'Corey Brewer': 201147,
              'Kyrie Irving': 202681, 'Darrell Arthur': 201589, 'Darrun Hilliard': 1626199, 'Jason Terry': 1891,
              'Thomas Robinson': 203080, 'David Lee': 101135, 'Giannis Antetokounmpo': 203507, 'Kenneth Faried': 202702,
              'Shaun Livingston': 2733, 'Branden Dawson': 1626183, 'Vince Carter': 1713, 'Kris Humphries': 2743,
              'Jared Cunningham': 203099, 'Miles Plumlee': 203101, 'Sonny Weems': 201603, 'CJ McCollum': 203468,
              'Tyler Ennis': 203898, 'Nick Young': 201156, 'Adreian Payne': 203940, 'PJ Tucker': 200782,
              'Kosta Koufos': 201585, 'Toney Douglas': 201962, 'Cole Aldrich': 202332, 'Anderson Varejao': 2760,
              'Norris Cole': 202708, 'Tyler Hansbrough': 201946, 'Mike Muscala': 203488, 'Justin Holiday': 203200,
              'Marvin Williams': 101107, 'Devin Booker': 1626164, 'Raul Neto': 203526, 'Jameer Nelson': 2749,
              'Bismack Biyombo': 202687, 'Deron Williams': 101114, 'Willie Cauley-Stein': 1626161,
              'Bobby Portis': 1626171, 'Mo Williams': 2590, 'Steve Blake': 2581, 'Patrick Beverley': 201976,
              'Udonis Haslem': 2617, 'KJ McDaniels': 203909, 'Karl-Anthony Towns': 1626157, 'Anthony Tolliver': 201229,
              'Kendall Marshall': 203088, 'Archie Goodwin': 203462, 'Taj Gibson': 201959, 'Anthony Davis': 203076,
              'Doug McDermott': 203926, 'Paul Pierce': 1718, 'Kevin Seraphin': 202338, 'John Wall': 202322,
              'Solomon Hill': 203524, 'Robin Lopez': 201577, 'Festus Ezeli': 203105, 'Tim Frazier': 204025,
              'Ish Smith': 202397, 'Pablo Prigioni': 203143, 'Lance Stephenson': 202362, "E'Twaun Moore": 202734,
              'Frank Kaminsky': 1626163, 'JJ Hickson': 201581, 'Brandon Knight': 202688, 'Carmelo Anthony': 2546,
              'Hollis Thompson': 203138, 'Jae Crowder': 203109, 'Spencer Hawes': 201150, 'Elfrid Payton': 203901,
              'Jeremy Lamb': 203087, 'Mirza Teletovic': 203141, 'Kyle Korver': 2594, 'Brandon Bass': 101138,
              'Nick Collison': 2555, 'Jose Calderon': 101181, 'JaMychal Green': 203210, 'LaMarcus Aldridge': 200746,
              'Robert Covington': 203496, 'Dewayne Dedmon': 203473, 'Luke Babbitt': 202337, 'Kyle Singler': 202713,
              'Hassan Whiteside': 202355, 'Anthony Morrow': 201627, "Amar'e Stoudemire": 2405, 'Ramon Sessions': 201196,
              'Quincy Acy': 203112, 'Ricky Rubio': 201937, 'Rudy Gay': 200752, 'Jahlil Okafor': 1626143,
              'Aaron Harrison': 1626151, 'Boris Diaw': 2564, 'Allen Crabbe': 203459, 'Brandon Jennings': 201943,
              'Drew Gooden': 2400, 'Dwyane Wade': 2548, 'Garrett Temple': 202066, 'Klay Thompson': 202691,
              'Patrick Patterson': 202335, 'Isaiah Canaan': 203477, 'Gordon Hayward': 202330, 'Marco Belinelli': 201158,
              'Markel Brown': 203900, 'Rodney Hood': 203918, 'JaKarr Sampson': 203960, 'Jabari Parker': 203953,
              'Chris Bosh': 2547, 'Jonas Valanciunas': 202685, 'Kyle Anderson': 203937, 'Pat Connaughton': 1626192,
              'Langston Galloway': 204038, 'Harrison Barnes': 203084, 'Robert Sacre': 203135, 'Ian Clark': 203546,
              'Seth Curry': 203552, 'James Michael McAdoo': 203949, 'Kelly Oubre': 1626162, "Johnny O'Bryant": 203948,
              'Bojan Bogdanovic': 202711, 'Omer Asik': 201600, "D'Angelo Russell": 1626156, 'Dante Cunningham': 201967,
              'Tristan Thompson': 202684, 'Marcelo Huertas': 1626273, 'Charlie Villanueva': 101111,
              'Marreese Speights': 201578, 'Chase Budinger': 201978, 'Tobias Harris': 202699, 'J.R. Smith': 2747,
              'Lou Williams': 101150, 'Eric Gordon': 201569, 'Dennis Schroder': 203471, 'Matt Bonner': 2588,
              'Ian Mahinmi': 101133, 'Clint Capela': 203991, 'Danny Green': 201980, 'Aaron Gordon': 203932,
              'Russell Westbrook': 201566, 'Trey Lyles': 1626168, 'Dirk Nowitzki': 1717, 'Luc Mbah a Moute': 201601,
              'DeMar DeRozan': 201942, 'Tim Duncan': 1495, 'Wayne Ellington': 201961, 'Richard Jefferson': 2210,
              'Mason Plumlee': 203486, 'Matt Barnes': 2440, 'Lance Thomas': 202498, 'Shabazz Napier': 203894,
              'Iman Shumpert': 202697, 'Andrew Nicholson': 203094, 'JJ Redick': 200755, 'Anthony Brown': 1626148,
              'Ryan Anderson': 201583, 'Joffrey Lauvergne': 203530, 'Serge Ibaka': 201586, 'Tyson Chandler': 2199,
              'Jerryd Bayless': 201573, 'Bruno Caboclo': 203998, 'Ryan Kelly': 203527, 'Carl Landry': 201171,
              'Jason Thompson': 201574, 'Tony Snell': 203503, 'Dion Waiters': 203079, 'Andre Miller': 1889,
              'Kent Bazemore': 203145, 'Nikola Jokic': 203999, 'Nemanja Bjelica': 202357, 'Tayshaun Prince': 2419,
              'DeJuan Blair': 201971, 'Terrence Ross': 203082, 'Ben McLemore': 203463, 'Gerald Henderson': 201945,
              'Andre Drummond': 203083, 'Nicolas Batum': 201587, 'Andrea Bargnani': 200745, 'Montrezl Harrell': 1626149,
              'James Anderson': 202341, 'Arron Afflalo': 201167, 'Cody Zeller': 203469, 'Marcus Morris': 202694,
              'Derrick Rose': 201565, 'Myles Turner': 1626167, 'Ronnie Price': 101179, 'Luis Scola': 2449,
              'Brian Roberts': 203148, 'Marcin Gortat': 101162, 'Kawhi Leonard': 202695, 'Channing Frye': 101112,
              'Devin Harris': 2734, 'Shane Larkin': 203499, 'Otto Porter': 203490, 'Darren Collison': 201954,
              'DeMarre Carroll': 201960, 'Nerlens Noel': 203457, 'Andre Iguodala': 2738, 'Stanley Johnson': 1626169,
              'Alonzo Gee': 202087, 'Evan Fournier': 203095, 'Mario Hezonja': 1626209, 'Jared Dudley': 201162,
              'John Henson': 203089, 'Trey Burke': 203504, 'Andre Roberson': 203460, 'Jusuf Nurkic': 203994,
              'Jonas Jerebko': 201973, 'Aron Baynes': 203382, 'Jarrett Jack': 101127, 'Markieff Morris': 202693,
              'Alex Len': 203458, 'Ryan Hollins': 200797, 'Dwight Howard': 2730, 'Matthew Dellavedova': 203521,
              'Patty Mills': 201988, 'Greg Monroe': 202328, 'Shabazz Muhammad': 203498, 'Kristaps Porzingis': 204001,
              'Chandler Parsons': 202718, 'Chris Andersen': 2365, 'Mitch McGary': 203956, 'Jose Juan Barea': 200826,
              'Ed Davis': 202334, 'Gerald Green': 101123, 'Nikola Mirotic': 202703, 'Joe Young': 1626202,
              'Victor Oladipo': 203506, 'Kevin Garnett': 708, 'D.J. Augustin': 201571, 'Jarell Eddie': 204067,
              'Andrew Bogut': 101106, 'Derrick Favors': 202324, 'Kendrick Perkins': 2570, 'Jrue Holiday': 201950,
              'Terrence Jones': 203093, 'Boban Marjanovic': 1626246, 'Jeremy Lin': 202391, 'Gary Harris': 203914,
              'Alexis Ajinca': 201582, 'Rashad Vaughn': 1626173, 'Paul George': 202331, 'CJ Miles': 101139}

player = args.player_w_underscore.replace("_"," ")
playerid = playerids[player]


def getFeaturesFromFile(filename):
    file = open(filename, 'r')
    data = json.load(file)
    file.close()
    features_from_file = []  # combined iso moments, to be eventually written to csv
    events = data['events']
    num_events = len(events)
    counter = 0
    # go through all events and look for iso defensive play
    for event in events:
        if len(event['moments']) == 0: continue
        new_event = ff.Event(event, int(playerid), teamids[args.team])
        player_in_event = False
        for playeridinevent in new_event.players_in_event:
            if playeridinevent == int(playerid): player_in_event = True
        if not player_in_event:
            print('Finished Event: ' + str(counter))
            counter += 1
            continue
        new_moments = new_event.findIsoMoments()
        if len(new_moments) > 0:
            for iso_moment in new_moments:
                features_from_file = features_from_file + iso_moment.convertFramesToFeatureVectors()
                features_from_file.append([])
        print('Finished Event: ' + str(counter))
        counter += 1
    return features_from_file

if __name__ == '__main__':
    
    to_csv = []
    movement_headers = ["PIQ_x_loc", "PIQ_y_loc", "PIQ_velocity", "PIQ_dx", "PIQ_dy", "PIQ_distance_from_hoop",
                        "BH_x_loc", "BH_y_loc", "BH_velocity", "BH_dx", "BH_dy", "BH_distance_from_hoop",
                        "GOLD_x_loc", "GOLD_y_loc"]
    game_counter = 1
    for filename in os.listdir("../data"):
        if fnmatch.fnmatch(filename, "*" + args.team + "*.7z"):
            os.system("7z e " + "../data/" + filename)
            for potential_json_file in os.listdir("."):
                if fnmatch.fnmatch(potential_json_file, "*.json"):
                    to_csv = to_csv + getFeaturesFromFile(potential_json_file)
            print("Done with game " + str(game_counter) + "!")
            game_counter += 1
            os.system("rm *.json")

    pd_list = pd.DataFrame(to_csv, columns=movement_headers)
    pd_list.to_csv('../data/csv/' + args.player_w_underscore + '.csv', index=False)





