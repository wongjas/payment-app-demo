from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import random
import string
import math

app = Flask(__name__, static_folder='static')
CORS(app)

# Store payments in memory (in production, this would be a database)
payments = []

def generate_transaction_id():
    """Generate a fake transaction ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@app.route('/')
def index():
    """Serve the main payment page"""
    return send_from_directory('static', 'index.html')

@app.route('/favicon.ico')
def favicon():
    """Return a 204 No Content for favicon requests"""
    return '', 204

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('static', filename)
    except:
        return '', 404

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """Process a fake payment"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['cardNumber', 'cardName', 'expiryDate', 'cvv', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Bug: Change False to True to fix the negative payment bug
        validate_positive = True
        
        amount = float(data['amount'])
        if validate_positive and amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
        
        # Simulate payment processing delay
        import time
        time.sleep(1)
        
        # Create payment record
        payment = {
            'transaction_id': generate_transaction_id(),
            'amount': amount,
            'currency': data.get('currency', 'USD'),
            'card_last_four': data['cardNumber'][-4:],
            'card_name': data['cardName'],
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        payments.append(payment)
        
        return jsonify({
            'success': True,
            'transaction_id': payment['transaction_id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'timestamp': payment['timestamp']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions"""
    return jsonify({
        'success': True,
        'transactions': payments
    })

@app.route('/api/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get a specific transaction"""
    transaction = next((p for p in payments if p['transaction_id'] == transaction_id), None)
    
    if transaction:
        return jsonify({
            'success': True,
            'transaction': transaction
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Transaction not found'
        }), 404

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 Fake Payment App Server Starting...")
    print("="*60)
    print("\n📱 Open your browser to: http://localhost:5000")
    print("\n💳 Test Card Numbers:")
    print("   • 4532 1488 0343 6467 (Visa)")
    print("   • 5425 2334 3010 9903 (Mastercard)")
    print("   • 3782 822463 10005 (Amex)")
    print("\n⚠️  Note: This is a FAKE payment system for prototyping only!")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)

