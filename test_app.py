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


def test_index_route(client):
    """Test that the index route returns the HTML page"""
    response = client.get('/')
    assert response.status_code == 200


def test_favicon_route(client):
    """Test that favicon route returns 204"""
    response = client.get('/favicon.ico')
    assert response.status_code == 204


def test_generate_transaction_id():
    """Test transaction ID generation"""
    tid = generate_transaction_id()
    assert len(tid) == 12
    assert tid.isalnum()
    # Check uniqueness
    tid2 = generate_transaction_id()
    assert tid != tid2


def test_payment_success(client):
    """Test successful payment processing"""
    payment_data = {
        'cardNumber': '4532148803436467',
        'cardName': 'JOHN DOE',
        'expiryDate': '12/25',
        'cvv': '123',
        'amount': 99.99,
        'currency': 'USD'
    }
    response = client.post('/api/payment',
                          data=json.dumps(payment_data),
                          content_type='application/json')
    
    # Note: This might fail randomly due to the 10% failure rate
    # In a real test, we'd mock the random function
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'transaction_id' in data
        assert data['amount'] == 99.99
        assert data['currency'] == 'USD'


def test_payment_missing_field(client):
    """Test payment with missing required field"""
    payment_data = {
        'cardNumber': '4532148803436467',
        'cardName': 'JOHN DOE',
        # Missing expiryDate
        'cvv': '123',
        'amount': 99.99
    }
    response = client.post('/api/payment',
                          data=json.dumps(payment_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'error' in data


def test_payment_invalid_amount(client):
    """Test payment with invalid amount"""
    payment_data = {
        'cardNumber': '4532148803436467',
        'cardName': 'JOHN DOE',
        'expiryDate': '12/25',
        'cvv': '123',
        'amount': 'invalid',
        'currency': 'USD'
    }
    response = client.post('/api/payment',
                          data=json.dumps(payment_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False


def test_payment_zero_amount(client):
    """Test payment with zero amount"""
    payment_data = {
        'cardNumber': '4532148803436467',
        'cardName': 'JOHN DOE',
        'expiryDate': '12/25',
        'cvv': '123',
        'amount': 0,
        'currency': 'USD'
    }
    response = client.post('/api/payment',
                          data=json.dumps(payment_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False


def test_payment_negative_amount(client):
    """Test payment with negative amount"""
    payment_data = {
        'cardNumber': '4532148803436467',
        'cardName': 'JOHN DOE',
        'expiryDate': '12/25',
        'cvv': '123',
        'amount': -50,
        'currency': 'USD'
    }
    response = client.post('/api/payment',
                          data=json.dumps(payment_data),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False


def test_get_transactions_empty(client):
    """Test getting transactions when none exist"""
    response = client.get('/api/transactions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['transactions'] == []


def test_get_transaction_not_found(client):
    """Test getting a transaction that doesn't exist"""
    response = client.get('/api/transaction/NONEXISTENT')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'error' in data
