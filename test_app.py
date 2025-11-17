import pytest
import json
from app import app, payments, generate_transaction_id


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Clear payments after each test
    payments.clear()


class TestPaymentAPI:
    """Test cases for the payment API endpoints"""
    
    def test_index_route(self, client):
        """Test that the index route serves the HTML page"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'SecurePay' in response.data
    
    def test_favicon_route(self, client):
        """Test that favicon route returns 204"""
        response = client.get('/favicon.ico')
        assert response.status_code == 204
    
    def test_successful_payment(self, client):
        """Test a successful payment transaction"""
        payment_data = {
            'cardNumber': '4532148803436467',
            'cardName': 'TEST USER',
            'expiryDate': '12/25',
            'cvv': '123',
            'amount': 99.99,
            'currency': 'USD'
        }
        
        response = client.post('/api/payment',
                              data=json.dumps(payment_data),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        # Check response
        assert response.status_code == 200
        assert data['success'] is True
        assert 'transaction_id' in data
        assert data['amount'] == 99.99
        assert data['currency'] == 'USD'
        
        # Check that payment was stored
        assert len(payments) == 1
        assert payments[0]['amount'] == 99.99
    
    def test_negative_payment_rejected(self, client):
        """Test that negative payments are properly rejected"""
        payment_data = {
            'cardNumber': '4532148803436467',
            'cardName': 'TEST USER',
            'expiryDate': '12/25',
            'cvv': '123',
            'amount': -50.00,
            'currency': 'USD'
        }
        
        response = client.post('/api/payment',
                              data=json.dumps(payment_data),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        # Negative payments should be rejected
        assert response.status_code == 400
        assert data['success'] is False
        assert 'error' in data
        # Check that error message mentions amount validation
        error_msg = data['error'].lower()
        assert 'amount' in error_msg or 'negative' in error_msg or 'invalid' in error_msg or 'greater' in error_msg
    
    def test_missing_fields(self, client):
        """Test that missing required fields return error"""
        payment_data = {
            'cardNumber': '4532148803436467',
            'cardName': 'TEST USER',
            # Missing expiryDate, cvv, amount
        }
        
        response = client.post('/api/payment',
                              data=json.dumps(payment_data),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'error' in data
    
    def test_get_all_transactions(self, client):
        """Test getting all transactions"""
        # First, create some transactions
        payment_data = {
            'cardNumber': '4532148803436467',
            'cardName': 'TEST USER',
            'expiryDate': '12/25',
            'cvv': '123',
            'amount': 25.50,
            'currency': 'USD'
        }
        
        client.post('/api/payment',
                   data=json.dumps(payment_data),
                   content_type='application/json')
        
        # Get all transactions
        response = client.get('/api/transactions')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['transactions']) == 1
        assert data['transactions'][0]['amount'] == 25.50
    
    def test_get_specific_transaction(self, client):
        """Test getting a specific transaction by ID"""
        # Create a transaction
        payment_data = {
            'cardNumber': '4532148803436467',
            'cardName': 'TEST USER',
            'expiryDate': '12/25',
            'cvv': '123',
            'amount': 75.00,
            'currency': 'USD'
        }
        
        response = client.post('/api/payment',
                              data=json.dumps(payment_data),
                              content_type='application/json')
        
        transaction_id = json.loads(response.data)['transaction_id']
        
        # Get the specific transaction
        response = client.get(f'/api/transaction/{transaction_id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['transaction']['transaction_id'] == transaction_id
        assert data['transaction']['amount'] == 75.00
    
    def test_transaction_not_found(self, client):
        """Test getting a non-existent transaction"""
        response = client.get('/api/transaction/INVALID123')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_generate_transaction_id(self):
        """Test that transaction IDs are generated correctly"""
        transaction_id = generate_transaction_id()
        
        assert len(transaction_id) == 12
        assert transaction_id.isalnum()
        assert transaction_id.isupper() or transaction_id.isdigit()
    
    def test_multiple_payments(self, client):
        """Test multiple payments are stored correctly"""
        payment_amounts = [10.00, 25.50, 99.99]
        
        for amount in payment_amounts:
            payment_data = {
                'cardNumber': '4532148803436467',
                'cardName': 'TEST USER',
                'expiryDate': '12/25',
                'cvv': '123',
                'amount': amount,
                'currency': 'USD'
            }
            
            client.post('/api/payment',
                       data=json.dumps(payment_data),
                       content_type='application/json')
        
        # Get all transactions
        response = client.get('/api/transactions')
        data = json.loads(response.data)
        
        assert len(data['transactions']) == 3
        stored_amounts = [t['amount'] for t in data['transactions']]
        assert sorted(stored_amounts) == sorted(payment_amounts)
    
    def test_card_last_four_stored(self, client):
        """Test that only last 4 digits of card are stored"""
        payment_data = {
            'cardNumber': '4532148803436467',
            'cardName': 'TEST USER',
            'expiryDate': '12/25',
            'cvv': '123',
            'amount': 50.00,
            'currency': 'USD'
        }
        
        response = client.post('/api/payment',
                              data=json.dumps(payment_data),
                              content_type='application/json')
        
        # Check stored payment
        assert len(payments) == 1
        assert payments[0]['card_last_four'] == '6467'
        assert 'cardNumber' not in payments[0]  # Full card number not stored

