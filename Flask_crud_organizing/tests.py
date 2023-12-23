import unittest
from flask import Flask
from flask_testing import TestCase
from app import app ,mysql
import json
import xml.etree.ElementTree as ET 
class TestApp(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
    
    def assert_json(self, response):
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    def assert_xml(self, response):
        data = ET.fromstring(response.data)
        self.assertIsInstance(data, ET.Element)
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        return app

    def test_index_default_format(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assert_json(response)

    def test_index_json_format(self):
        response = self.client.get('/?format=json')
        self.assertEqual(response.status_code, 200)
        self.assert_json(response)

    def test_index_xml_format(self):
        response = self.client.get('/?format=xml')
        self.assertEqual(response.status_code, 200)
        self.assert_xml(response)
    def test_valid_user_login(self):
        # Replace this with a valid email from your test data or database
        valid_user_email = 'joshua.doe@example.com'

        response = self.app.post('/login', data=dict(email=valid_user_email))

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check that the response contains an 'access_token'
        self.assertIn('access_token', response.json)

    def test_invalid_user_login(self):
        # Replace this with an invalid email that does not exist in your database
        invalid_user_email = 'invalid_user@example.com'

        response = self.app.post('/login', data=dict(email=invalid_user_email))
        
        print(response.status_code)
        print(response.json)
        # Check that the response status code is 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        # Check that the response contains an 'error' message
        self.assertIn('error', response.json)

    def test_insert(self):
        response = self.client.post('/insert_customers', data={
            'customer_id': '52',
            'customer_first_name': 'Grececee',
            'customer_middle_initial': 'G',
            'customer_last_name': 'Tibudan',
            'email_address': 'joshua.doe@example.com',
            'gender': 'F',
            'phone_number': '123456787850',
            'address': 'Tiniguiban'
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful insertion


    def test_delete(self):
        response = self.client.get('/delete_customers/52')  # Replace '1' with an actual customer_id
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful deletion

    def test_update(self):
        response = self.client.post('/update_customers', data={
            'customer_id': '2',  # Replace '1' with an actual customer_id
            'customer_first_name': 'Alyanaa',
            'customer_middle_initial': 'U',
            'customer_last_name': 'Doe',
            'email_address': 'ilyana.email@example.com',
            'gender': 'F',
            'phone_number': '9876543210',
            'address' : 'Tiniguiban'
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful update


    def setUp(self):
        # Create a test client
        self.client = app.test_client()

    def test_search_by_name(self):
        response = self.client.get('/search?criteria=John')  # Search by first name only
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        
        # Adjust this assertion based on your actual expectations for the default output format
        self.assertIn('customers', data)
        self.assertEqual(len(data['customers']), 1)
