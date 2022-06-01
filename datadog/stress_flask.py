import requests
import sys

def run_stress(i):
    if i == -1:
        for i in range(0, 10):
            run_stress(i)
    elif i % 10 == 0:
        if i == 0:
            i = 10
        requests.post(url + 'kafka', json={'round': str(i)})
        print('POST Kafa: ' + str(i))
    elif i % 5 == 0:
        requests.post(url + 'items/', json={'title': 'Title ' + str(i), 'content': 'Content ' + str(i)})
        print('POST Item: ' + str(i))
    else:
        requests.get(url + 'items/')
        print('GET Item: ' + str(i))
    requests.get(url)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s <int>' % sys.argv[0])
        sys.exit(1)

    url = 'http://localhost:5000/'
    if sys.argv[1] == '-1':
        while True:
            run_stress(int(sys.argv[1]))
    else:
        for i in range(0,int(sys.argv[1])):
            run_stress(i)

