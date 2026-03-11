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



def select_tasks(map, island, number_of_capitols):

    tasks = random.sample(TASKS, 3)

    number_of_crossroad_tasks = 0
    number_of_castles = 0
    number_of_palaces = 0

    if island:
        number_of_castles += 1

    for map_tile in map:
        if map_tile[1] == "C":
            number_of_crossroad_tasks += 1
        number_of_palaces += map_tile[4]
        number_of_castles += map_tile[3]

    crossroad_tasks = random.sample(CROSSROAD_TASKS, number_of_crossroad_tasks)
    tasks = tasks + crossroad_tasks

    if "Noblewomen" not in tasks and number_of_palaces > 0:
        tasks += ["task_palaces"]
    if number_of_castles - number_of_capitols > 0:
        tasks += ["task_castles"]
    if number_of_capitols > 0 and number_of_castles > 0:
        tasks += ["task_capitols"]
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
    return random.choice(["wood", "canyon"])

#TODO: get random number for map tile position of each cave
def caves_queenie():
        return "caves"

#TODO: get random number(s) for capitol(s)
def capitols_queenie():
    both_capitols = random.choice([True, False])
    if both_capitols:
        return 2
    else:
        return 1


#fyi: Lords excluded
TASKS = [
    "task_fishermen",
    "task_miners",
    "task_merchants",
    "task_workers",
    "task_discoverer",
    "task_knights",
    "task_hermits",
    "task_citizens",
    "task_farmers",
    "task_families",
    "task_shepherds",
    "task_ambassadors",
    "task_geologists",
    "task_messengers",
    "task_noblewomen",
    "task_vassals",
    "task_captains",
    "task_scouts",
    "task_rangers",
    "task_travellers",
    "task_chainers",
    "task_homesteaders",
    "task_mayors",
    "task_rovers"
]
CROSSROAD_TASKS = [
    "crossroad_task_home_country",
    "crossroad_task_place_of_refuge",
    "crossroad_task_fortress",
    "crossroad_task_advance",
    "crossroad_task_road",
    "crossroad_task_compass_points"
]


# [ID, "expansion", "title", castles, palaces, Silos, Mountain Caves]
MAP_TILES = [
    [1, "KB", "map_oracle", 2, 0, 0, 2],
    [2, "KB", "map_harbor", 2, 0, 0, 1],
    [3, "KB", "map_oasis", 1, 0, 0, 0],
    [4, "KB", "map_paddock", 1, 0, 0, 13],
    [5, "KB", "map_barn", 1, 0, 0, 9],
    [6, "KB", "map_tower", 1, 0, 0, 9],
    [7, "KB", "map_farm", 1, 0, 0, 2],
    [8, "KB", "map_tavern", 1, 0, 0, 9],
    [9, "N", "map_quarry", 0, 0, 0, 3],
    [10, "N", "map_village", 0, 0, 0, 4],
    [11, "N", "map_garden", 0, 0, 0, 5],
    [12, "N", "map_caravan", 0, 0, 0, 1],
    [13, "C", "map_lighthouse", 1, 0, 0, 3],
    [14, "C", "map_fort", 1, 0, 0, 6],
    [15, "C", "map_wagon", 1, 0, 0, 6],
    [16, "C", "map_crossroads", 1, 0, 0, 1],
    [17, "H", "map_watchtower", 0, 0, 1, 1],
    [18, "H", "map_scout_cabin", 1, 0, 1, 2],
    [19, "H", "map_water_mill", 0, 0, 1, 6],
    [20, "H", "map_palisade", 0, 0, 1, 3],
    [21, "M", "map_refuge", 0, 1, 0, 6],
    [22, "M", "map_temple", 0, 1, 0, 1],
    [23, "M", "map_fountain", 0, 1, 0, 2],
    [24, "M", "map_canoe", 0, 1, 0, 7]
]

def create_match():

    output = datetime.datetime.today()
    output = output.strftime("%x")+ "\n"

    # Queenies
    island = 0
    caves = 0
    capitols = 0

    #   Island (Queenie 3)
    if random.choice([True, False]):
        island = island_queenie()
        #output += island + "\n"
    #   Caves (Queenie 2)
    if random.choice([True, False]):
        caves = caves_queenie()
        #output += str(caves) + "\n"
    #   Capitol (Queenie 1)
    if random.choice([True, False]):
        capitols = capitols_queenie()
        #output += str(capitols) + "\n"

    # map
    map = select_map_tiles()

    # tasks
    tasks = select_tasks(map, island, capitols)



    output += str(map) + "\n"
    output += str(tasks) + "\n"

    print(output)

    return {
        "board_game_id": 1,
        "map": map,
        "tasks": tasks,
        "island": str(island),
        "caves": str(caves),
        "capitols": str(capitols)
    }