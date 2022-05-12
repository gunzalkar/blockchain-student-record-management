from flask import Flask, render_template, redirect, flash, request, jsonify, url_for
from config import Config
import hashlib
import json
from blockchain import blockchain, node_address
from forms import BasicForm, SearchForm, LoginForm
import argparse
import subprocess


app = Flask(__name__)
app.config.from_object(Config)
password_hash = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'


def get_arguments():
	parser = argparse.ArgumentParser(description='Arguments for Blockchain app')
	parser.add_argument('-ah', '--host', dest='app_host', help="Host to run application on")
	parser.add_argument('-p', '--port', dest='app_port', type=int, help="Port to run application on")

	return parser.parse_args()

args = get_arguments()
host = args.app_host
port = args.app_port
server_number = str(port)[-1]
is_logged_in=False

def ping_servers(nodes_list):
    response = []
    if nodes_list is None:
        return False
    for node in nodes_list:
        url = f'http://{node}'
        print(f'Pinging url {url}')
        try:
            output = str(subprocess.check_output(['curl', '-Is', url]).decode('utf-8')).split('\n')[0]
            print(f'Output: {output}')
            if output[9:12] == '200':
                server_response = {
                    'address'   : node,
                    'output'    : 'Up'
                }
                response.append(server_response)
            else:
                server_response = {
                    'address'   : node,
                    'output'    : 'Down'
                }
                response.append(server_response)
        except:
            server_response = {
                'address'   : node,
                'output'    : 'Down'
            }
            response.append(server_response)
    return response

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        form_username = form.username.data
        form_password = form.password.data
        form_password_hash = hashlib.sha256(str(form_password).encode()).hexdigest()

        if form_username == 'admin' and form_password_hash == password_hash:
            flash('Login Successfull', 'success')
            return redirect(url_for('index'))
        else:
            flash('Sorry Invalid Credentials', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)

@app.route('/home')
def index():
    return render_template('home.html', title='HomePage', blockchain_nodes=blockchain.nodes, address=node_address, server_number=server_number)
	
@app.route('/register', methods=['GET' ,'POST'])
def register():
	form = BasicForm()
	if form.validate_on_submit():
		student_data_record = {
			'f_name'	: form.f_name.data,
			'l_name' 	: form.l_name.data,
			'email'		: form.email.data,
			'address'	: form.address.data,
			'batch'		: form.batch.data,
			'roll_no'	: form.roll_no.data,
			'enrollment_no'	: form.enrollment_no.data
		}
		previous_block = blockchain.get_previous_block() 
		previous_block_hash = blockchain.hash(previous_block)
		new_block = blockchain.create_block(student_data_record, previous_block_hash)
		response = {
			'Message'	: 'New block has been added successfully',
			'Block'		: new_block
		}
		return render_template('block.html', block=new_block)
	return render_template('register.html', title='Register', form=form)

@app.route('/show_chain', methods=['GET'])
def show_chain():
    hash = blockchain.hash
    synched = blockchain.is_chain_synched()
    show_sync_button = False
    if not synched:
        flash(f'Chain is not up to date. Please synchronize', 'danger')
        show_sync_button = True
    return render_template('chain.html', chain=blockchain.chain, title='MainChain', hash=hash,show_sync_button=show_sync_button)

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'Message'   : 'Here is your Chain',
        'Chain'     : blockchain.chain,
        'Host'      : host,
        'Port'      : port,
        'Length'    : len(blockchain.chain)
    }    
    return jsonify(response)

@app.route('/validity')
def validity():
	validity = blockchain.is_chain_valid(blockchain.chain)
	if validity:
		response = {
			'Message' : 'Chain is valid',
			'Chain'	: blockchain.chain 
		}
	else:
		response = {
			'Message' : 'Chain is invalid',
			'Chain'	: blockchain.chain
		}
	return jsonify(response)

@app.route('/is_chain_valid')
def check_chain_validity():
	validity = blockchain.is_chain_valid(blockchain.chain)
	if validity:
		flash('Blockchain is well and fine. Go ahead with your work.', 'success')
	else:
		flash('Well something seems wrong with the chain. Do take a look', 'danger')
	return redirect(url_for('show_chain'))

@app.route('/connect_node', methods=['POST'])
def connect_node():
    json_file = request.get_json()
    nodes = json_file.get('nodes')
    if nodes is None:
        return 'Sorry no Nodes Found', 400
    for node in nodes:
        blockchain.add_node(node)
    response ={
        'Message'   : 'All the nodes have been added Successfully.',
        'Nodes'     : list(blockchain.nodes)
    }
    return jsonify(response)

@app.route('/replace_chain')
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        flash(f'Chain was replaced successfully. Continue with your work', 'success')
    else:
        flash(f'Chain is up to date. No need to change.', 'info')
    return redirect(url_for('show_chain'))

@app.route('/servers')
def servers():
    nodes = list(blockchain.nodes)
    nodes.append('127.0.0.1:5004')
    response = ping_servers(nodes)
    if not response:
        flash('Looks like the network is not connected', 'danger')
        return redirect(url_for('index'))
    print(response)
    return render_template('servers.html', title='Servers', response=response)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        answer_block = None
        enroll = str(form.enrollment.data).lower()
        print(enroll)
        if enroll[:4] == 'mitu':
            for block in blockchain.chain:
                if str(block.get('enrollment_no')).lower() == enroll:
                    answer_block = block
                    break
            return render_template('block.html', title='Block', block=answer_block)
        else:
            flash('Sorry. The enrollment format is wrong', 'danger')
            return redirect('search')
    return render_template('search.html', title='Search', form=form)


app.run(host=host, port=port)