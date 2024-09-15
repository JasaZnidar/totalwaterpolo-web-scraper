import json
import copy

with open("miniBatch.json", "r") as f:
    data = json.load(f)

dates = [199680, 199687, 199694, 199701, 199708, 199715, 199722, 199729, 199736, 199743, 199750, 199757, 199764, 199771, 199778]
matches = [[(2, 3), (4, 5)], [(1, 5), (3, 4)], [(1, 4), (2, 5)], [(1, 2), (3, 5)], [(1, 3), (2, 4)],
           [(2, 3), (4, 5)], [(1, 5), (3, 4)], [(1, 4), (2, 5)], [(1, 2), (3, 5)], [(1, 3), (2, 4)],
           [(1, 2), (3, 4)], [(1, 2), (3, 4)], [(1, 2), (3, 4)]]
names = {
    1: "Ena",
    2: "Dva",
    3: "Tri",
    4: "Štiri",
    5: "Pet"
}
teams = ['home', 'away']
cnt = 1

template = {
      "competition id": "1",
      "date": 199680,
      "lineup": {
        "away": {
          "1": {
            "id": ""
          },
          "10": {
            "id": ""
          },
          "11": {
            "id": ""
          },
          "12": {
            "id": ""
          },
          "13": {
            "id": ""
          },
          "2": {
            "id": ""
          },
          "3": {
            "id": ""
          },
          "4": {
            "id": ""
          },
          "5": {
            "id": ""
          },
          "6": {
            "id": ""
          },
          "7": {
            "id": ""
          },
          "8": {
            "id": ""
          },
          "9": {
            "id": ""
          }
        },
        "home": {
          "1": {
            "id": ""
          },
          "10": {
            "id": ""
          },
          "11": {
            "id": ""
          },
          "12": {
            "id": ""
          },
          "13": {
            "id": ""
          },
          "2": {
            "id": ""
          },
          "3": {
            "id": ""
          },
          "4": {
            "id": ""
          },
          "5": {
            "id": ""
          },
          "6": {
            "id": ""
          },
          "7": {
            "id": ""
          },
          "8": {
            "id": ""
          },
          "9": {
            "id": ""
          }
        }
      },
      "name": {
        "away": "",
        "home": ""
      },
      "plays": [
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 2,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 54
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 3,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 108
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 2,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 162
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 4,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 216
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 5,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 270
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 3,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 324
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 6,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 278
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 7,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 432
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 4,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 486
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 8,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 540
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 9,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 594
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 5,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 648
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 10,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 702
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 11,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 756
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 6,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 810
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 12,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 864
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 2,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 918
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 7,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 972
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 3,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1026
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 4,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1080
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 8,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 1134
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 5,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1188
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 6,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1242
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 9,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 1296
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 7,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1350
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 8,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1404
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 10,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 1458
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 9,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1512
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 10,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1566
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 11,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 1620
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 11,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1674
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 12,
          "player_2": 0,
          "target": [0, 0],
          "team": "home",
          "time": 1728
        },
        {
          "action": "goal scored",
          "details": "",
          "location": [0, 0],
          "player_1": 12,
          "player_2": 0,
          "target": [0, 0],
          "team": "away",
          "time": 1782
        }
      ],
      "result": {
        "away": 11,
        "home": 22
      }
    }

for week in range(len(matches)):
    for match in range(len(matches[week])):
        
        m = copy.deepcopy(template)
        
        m['date'] = dates[week]
        m['name']['home'] = names[matches[week][match][0]]
        m['name']['away'] = names[matches[week][match][1]]
        
        for team in range(2):
            for player in range(len(m['lineup'][teams[team]])):
                m['lineup'][teams[team]][str(player+1)]['id'] = str( (matches[week][match][team] - 1)*13 + player + 1 )
        
        
        print(f"{str(cnt)} => {m['name']['home']} vs. {m['name']['away']}")
        data['matches'][str(cnt)] = dict(m)
        print(f"\t {data['matches'][str(cnt)]['name']['home']} vs. {data['matches'][str(cnt)]['name']['away']}")
        cnt += 1

with open("miniBatch.json", "w") as f:
    json.dump(data, f, sort_keys=True, indent=4)