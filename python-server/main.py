from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
	f = open('/data/logs/rf24network-server/rf24network_rx.log', 'r')
	log = f.read()
	f.close()
	return log

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=3000)
