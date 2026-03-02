from app import app

with app.test_client() as client:
    response = client.get('/')
    print('Status:', response.status_code)
    print('Content Length:', len(response.data))
    print('First 200 chars:', response.data[:200])
