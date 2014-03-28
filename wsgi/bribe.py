from flask import Flask, render_template, request
from config import callback_addr, recv_addr

import redis
import requests

app = Flask(__name__)
red = redis.Redis()

#app.debug = True

@app.route('/')
def hello_world():
    return 'Hello'

@app.route('/bribe/<command>')
def bribe(command=None):
    #if not request.args['prase']: return 'please specify phrase'
    if command == 'test':
        r = requests.get('https://blockchain.info/api/receive', 
                params={'method': 'create', 
                    'address': recv_addr, 
                    'callback': callback_addr,
                    'command': 'test'})
        input_address = r.json()['input_address']
        red.sadd('bribes', 'bribe.%s' % (input_address,))
        red.set('bribe.%s' % (input_address,), str(request.args['phrase']))
#   return '%s %s' % (input_address, request.args['phrase'])
    return render_template('bribe.html', address=input_address, phrase=request.args['phrase'])
        

@app.route('/callback')
def callback():
    input_address = request.args['input_address']
    if request.args['address'] == '1L28tSa2nobWwh5QPyLg8ryx6JN14GrBHr':
        phrase = red.get('bribe.%s' % (input_address,))
        red.sadd('bribes:paid', 'bribe.%s' % (input_address,))
        red.rpush('wcards:override', phrase)
    return '*ok*'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
