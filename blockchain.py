from flask import Flask, jsonify, request
import hashlib # for encryption
import json # for block formatting
from time import time # for each block's timestamp
import uuid

class Blockchain(object):

    def __init__(self):
        # Empty list to store blocks --> The Blockchain
        self.chain = []
        # Pending transactions being requested are stored in this list, then added to a new block once verified
        self.pending_transactions = []
        # call to add each block to the blockchain --> Genesis block
        # proof=100 is arbitrary
        self.new_block(previous_hash="The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.", proof=100)

    def proof_of_work(self, last_proof):
        """This method is where you the consensus algorithm is implemented.
        It takes two parameters including self and last_proof"""
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """This method validates the block"""

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"
    
    def new_block(self, proof, previous_hash=None):
        #This function creates new blocks and then adds to the existing chain
        """This method creates new blocks and then adds to the existing chain"""
        # block Dictionary which holds important info for each block
        block = {
            # Index for blockchain starts at 1 instead of 0 --> take length of the blockchain and add 1 to it
            'index': len(self.chain) + 1,
            'timestamp' : time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Set the current transaction list to empty.
        self.pending_transactions=[]
        self.chain.append(block)

        return block
    
    @property
    def last_block(self):
        # Calls and returns the last block of the chain: last block in the list
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        #This function adds a new transaction to already existing transactions
        """This will create a new transaction which will be sent to the next block. It will contain
            three variables including sender, recipient and amount"""

        # Adding transactions to pending list: waiting to be verified
        self.pending_transactions.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
            }
        )
        # Return the index of the block our new transaction would be added to.
        # Since it hasn't been added yet, we will add the transaction to the next block.
        # Finding which block the transaction was created
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        #Used for hashing a block
        # """The following code will create a SHA-256 block hash and also ensure that the dictionary is ordered"""
        # block_string = json.dumps(block, sort_keys=True).encode()
        # return hashlib.sha256(block_string).hexdigest()
        string_object = json.dumps(block, sort_keys=True)

        # convert string into bytes for the hash function
        block_string = string_object.encode()
        # secure hash algorithm (sha)
        raw_hash = hashlib.sha256(block_string)

        # Return the encoded data in hexadecimal format
        hex_hash = raw_hash.hexdigest()

        return hex_hash



# Creating the app node
app = Flask(__name__)
node_identifier = str(uuid.uuid4()).replace('-',"")

# Initializing blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():

    """Here we make the proof of work algorithm work"""

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # rewarding the miner for his contribution. 0 specifies new coin has been mined

    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
    )

    # now create the new block and add it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'The new block has been forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash' : block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['GET','POST'])
def new_transaction():

    values = request.get_json(force=True)

    # Checking if the required data is there or not
    required = ['sender','recipient','amount']

    if not all(k in values for k in required):
        return 'Missing values', 400

    # creating a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction is scheduled to be added to Block No. {index}'}

    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():

    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain)
    }

    return jsonify(response), 200


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=5000)