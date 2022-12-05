import json

f = open('singapore_covid_cases.json')

data = json.load(f)

f.close()

processed_data_list = []
processed_data = []

processed_data.append(data[0]['Date'])
processed_data.append(data[0]['Cases'])
processed_data.append(data[0]['Cases'])

processed_data_list.append(processed_data)

for i in range(1,len(data)):
    processed_data = []
    processed_data.append(data[i]['Date'])
    processed_data.append(data[i]['Cases'])
    processed_data.append(data[i]['Cases'] - data[i-1]['Cases'])
    processed_data_list.append(processed_data)

for k in processed_data_list:
    print(k)
