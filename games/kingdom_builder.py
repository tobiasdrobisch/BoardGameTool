import random
import datetime



setup_guide = ""


def select_map_tiles():
    selected = random.sample(MAP_TILES, 4)
    orientation = ["reversed", "upright"]
    map = []

    for tile in selected:
        tile_copy = tile.copy()
        tile_copy.append(random.choice(orientation))
        map.append(tile_copy)

    return map


def select_tasks(map):
    number_of_crossroad_tasks = 0
    for map_tile in map:
        if map_tile[1] == "C":
            number_of_crossroad_tasks += 1
    crossroad_tasks = random.sample(CROSSROAD_TASKS, number_of_crossroad_tasks)
    tasks = random.sample(TASKS, 3)
    tasks = tasks + crossroad_tasks
    return tasks

def nomads_expansion():
    pass

def crossroads_expansion():
    pass

def marshlands_expansion():
    pass

def harvest_expansion():
    pass

def island_queenie():
    return random.choice(["Wood", "Canyon"])

#TODO: get random number for map tile position of each cave
def caves_queenie():
        return 'caves'

#TODO: get random number(s) for capitol(s)
def capitols_queenie():
    both_capitols = random.choice([True, False])
    if both_capitols:
        return 'both capitols'
    else:
        return 'one capitol'


#TODO: change to english words?
TASKS = ["Fischer", "Bergleute", "Händler", "Arbeiter", "Entdecker", "Ritter", "Einsiedler", "Bürger", "Bauern", "Familien", "Hirten", "Botschafter", "Geologen", "Boten", "Adel", "Vasallen", "Hauptmänner", "Späher", "Waldläufer", "Abenteurer", "Wirt", "Landbesitzer", "Bürgermeister", "Vagabund"]
CROSSROAD_TASKS = ["Heimatland", "Zufluchtsort", "Festung", "Vormarsch", "Straße", "Himmelsrichtungen"]

# [ID, "expansion", "title", # (placeholder), castles, palaces, Silos, Höhlengebirge]
MAP_TILES = [
    [1, "KB", "Orakel"], #, 2, 0, 0, 2
    [2, "KB", "Schiff"], #, 2, 0, 0, 1
    [3, "KB", "Oase"], # , 1, 0, 0, 0
    [4, "KB", "Pferde"], #, 1, 0, 0, 13
    [5, "KB", "Bauernhof"], #, 1, 0, 0, 9
    [6, "KB", "Türme"], #, 1, 0, 0, 9
    [7, "KB", "Grasland"],#, 1, 0, 0, 2
    [8, "KB", "3zu4"], #, 1, 0, 0, 9
    [9, "N", "Mauern"],#, 0, 0, 0, 3
    [10, "N", "Stadt"], #, 0, 0, 0, 4
    [11, "N", "Gärten"], #, 0, 0, 0, 5
    [12, "N", "Kamele"], #, 0, 0, 0, 1
    [13, "C", "Leuchtturm"], #, 1, 0, 0, 3
    [14, "C", "Kapitol"], # , 1, 0, 0, 6  TODO: renaming to Rathaus?
    [15, "C", "Wagen"], #, 1, 0, 0, 6
    [16, "C", "Kreuzung"], #, 1, 0, 0, 1
    [17, "H", "Funkturm"], #, 0, 0, 1, 1
    [18, "H", "Späher"], #, 1, 0, 1, 2
    [19, "H", "Wassermühle"], #, 0, 0, 1, 6
    [20, "H", "Palisade"], #, 0, 0, 1, 3
    [21, "M", "Schloss"], #, 0, 1, 0, 6
    [22, "M", "Tempel"], #, 0, 1, 0, 1
    [23, "M", "Brunnen"],#, 0, 1, 0, 2
    [24, "M", "Kanu"], #, 0, 1, 0, 7
]

def create_match():

    output = datetime.datetime.today()
    output = output.strftime("%x")+ "\n"


    # map
    map = select_map_tiles()

    # tasks
    tasks = select_tasks(map)

    # Queenies
    island = "No"
    caves = "No"
    capitols = "No"

    #   Island (Queenie 3)
    if random.choice([True, False]):
        island = island_queenie()
        output += island + "\n"
    #   Caves (Queenie 2)
    if random.choice([True, False]):
        caves = caves_queenie()
        output += caves + "\n"
    #   Capitol (Queenie 1)
    if random.choice([True, False]):
        capitols = capitols_queenie()
        output += capitols + "\n"

    output += str(map) + "\n"
    output += str(tasks) + "\n"

    print(output)

    return {
        "board_game_id": 1,
        "map": map,
        "tasks": tasks,
        "island": island,
        "caves": caves,
        "capitols": capitols
    }