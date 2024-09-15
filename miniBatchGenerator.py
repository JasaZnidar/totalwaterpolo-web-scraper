import json

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

template = data['matches']['template']

for week in range(len(matches)):
    for match in range(len(matches[week])):
        
        template['date'] = dates[week]
        template['name']['home'] = names[matches[week][match][0]]
        template['name']['away'] = names[matches[week][match][1]]
        
        for team in range(2):
            for player in range(len(template['lineup'][teams[team]])):
                template['lineup'][teams[team]][str(player+1)]['id'] = str( (matches[week][match][team] - 1)*13 + player + 1 )
        
        data['matches'][str(cnt)] = dict(template)
        cnt += 1

with open("miniBatch.json", "w") as f:
    json.dump(data, f, sort_keys=True, indent=4)