import asyncio
import json
import os
import sys
from quart import Quart
from quart.testing import QuartClient
from dotenv import load_dotenv

# Add src directory to path
sys.path.append('./src')

from database import db_manager, ExcludedKeyword
from app import app

# Load environment variables
load_dotenv()

# Override database settings for tests (Docker postgres container)
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT_INTERNAL'] = '5433'  # External port for tests

class TestExcludedKeywordsAPI:
    """Integration tests for excluded keywords API endpoints"""
    
    def __init__(self):
        self.app = app
        self.client = None
        self.test_keywords = ['spam', 'test_keyword', 'интеграционный_тест']
    
    async def setup_method(self):
        """Setup method called before each test"""
        # Initialize database
        await db_manager.initialize()
        
        # Create test client
        self.client = self.app.test_client()
        
        # Clean up any existing test keywords
        await self.cleanup_test_keywords()
        
        # Create session for authentication
        async with self.client.session_transaction() as session:
            session['logged_in'] = True
    
    async def cleanup_test_keywords(self):
        """Clean up test keywords from database"""
        for keyword in self.test_keywords:
            await db_manager.remove_keyword(keyword)
    
    async def teardown_method(self):
        """Cleanup method called after each test"""
        await self.cleanup_test_keywords()
    
    async def test_get_excluded_keywords_empty(self):
        """Test GET /api/excluded_keywords with empty database"""
        response = await self.client.get('/api/excluded_keywords')
        assert response.status_code == 200
        
        data = await response.get_json()
        assert 'keywords' in data
        assert isinstance(data['keywords'], list)
        print(f"✓ GET /api/excluded_keywords (empty): {data}")
    
    async def test_get_excluded_keywords_with_data(self):
        """Test GET /api/excluded_keywords with existing data"""
        # Add some test keywords
        await db_manager.add_keyword('spam')
        await db_manager.add_keyword('test_keyword')
        
        response = await self.client.get('/api/excluded_keywords')
        assert response.status_code == 200
        
        data = await response.get_json()
        assert 'keywords' in data
        assert len(data['keywords']) == 2
        assert 'spam' in data['keywords']
        assert 'test_keyword' in data['keywords']
        print(f"✓ GET /api/excluded_keywords (with data): {data}")
    
    async def test_get_excluded_keywords_unauthorized(self):
        """Test GET /api/excluded_keywords without authentication"""
        # Create unauthenticated client
        async with self.client.session_transaction() as session:
            session.clear()
        
        response = await self.client.get('/api/excluded_keywords')
        assert response.status_code == 401
        
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Unauthorized'
        print(f"✓ GET /api/excluded_keywords (unauthorized): {data}")
    
    async def test_post_excluded_keyword_success(self):
        """Test POST /api/excluded_keywords with valid data"""
        keyword_data = {'keyword': 'spam'}
        
        response = await self.client.post(
            '/api/excluded_keywords',
            json=keyword_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = await response.get_json()
        assert 'message' in data
        assert data['message'] == 'Keyword added successfully'
        
        # Verify keyword was added to database
        assert await db_manager.keyword_exists('spam')
        print(f"✓ POST /api/excluded_keywords (success): {data}")
    
    async def test_post_excluded_keyword_empty(self):
        """Test POST /api/excluded_keywords with empty keyword"""
        keyword_data = {'keyword': ''}
        
        response = await self.client.post(
            '/api/excluded_keywords',
            json=keyword_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Keyword is required'
        print(f"✓ POST /api/excluded_keywords (empty): {data}")
    
    async def test_post_excluded_keyword_whitespace(self):
        """Test POST /api/excluded_keywords with whitespace-only keyword"""
        keyword_data = {'keyword': '   '}
        
        response = await self.client.post(
            '/api/excluded_keywords',
            json=keyword_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Keyword is required'
        print(f"✓ POST /api/excluded_keywords (whitespace): {data}")
    
    async def test_post_excluded_keyword_duplicate(self):
        """Test POST /api/excluded_keywords with duplicate keyword"""
        # Add keyword first
        await db_manager.add_keyword('spam')
        
        keyword_data = {'keyword': 'spam'}
        response = await self.client.post(
            '/api/excluded_keywords',
            json=keyword_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 400
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Keyword already exists'
        print(f"✓ POST /api/excluded_keywords (duplicate): {data}")
    
    async def test_post_excluded_keyword_unauthorized(self):
        """Test POST /api/excluded_keywords without authentication"""
        # Clear session
        async with self.client.session_transaction() as session:
            session.clear()
        
        keyword_data = {'keyword': 'spam'}
        response = await self.client.post(
            '/api/excluded_keywords',
            json=keyword_data,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 401
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Unauthorized'
        print(f"✓ POST /api/excluded_keywords (unauthorized): {data}")
    
    async def test_delete_excluded_keyword_success(self):
        """Test DELETE /api/excluded_keywords/{keyword} with existing keyword"""
        # Add keyword first
        await db_manager.add_keyword('spam')
        
        response = await self.client.delete('/api/excluded_keywords/spam')
        assert response.status_code == 200
        
        data = await response.get_json()
        assert 'message' in data
        assert data['message'] == 'Keyword removed successfully'
        
        # Verify keyword was removed from database
        assert not await db_manager.keyword_exists('spam')
        print(f"✓ DELETE /api/excluded_keywords/spam (success): {data}")
    
    async def test_delete_excluded_keyword_not_found(self):
        """Test DELETE /api/excluded_keywords/{keyword} with non-existing keyword"""
        response = await self.client.delete('/api/excluded_keywords/nonexistent')
        assert response.status_code == 404
        
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Keyword not found'
        print(f"✓ DELETE /api/excluded_keywords/nonexistent (not found): {data}")
    
    async def test_delete_excluded_keyword_unauthorized(self):
        """Test DELETE /api/excluded_keywords/{keyword} without authentication"""
        # Clear session
        async with self.client.session_transaction() as session:
            session.clear()
        
        response = await self.client.delete('/api/excluded_keywords/spam')
        assert response.status_code == 401
        
        data = await response.get_json()
        assert 'error' in data
        assert data['error'] == 'Unauthorized'
        print(f"✓ DELETE /api/excluded_keywords/spam (unauthorized): {data}")
    
    async def test_delete_excluded_keyword_with_spaces(self):
        """Test DELETE /api/excluded_keywords/{keyword} with spaces in keyword"""
        # Add keyword with spaces
        keyword_with_spaces = 'test keyword'
        await db_manager.add_keyword(keyword_with_spaces)
        
        # URL encode the keyword
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword_with_spaces)
        
        response = await self.client.delete(f'/api/excluded_keywords/{encoded_keyword}')
        assert response.status_code == 200
        
        data = await response.get_json()
        assert 'message' in data
        assert data['message'] == 'Keyword removed successfully'
        
        # Verify keyword was removed
        assert not await db_manager.keyword_exists(keyword_with_spaces)
        print(f"✓ DELETE /api/excluded_keywords/{encoded_keyword} (with spaces): {data}")
    
    async def test_full_crud_workflow(self):
        """Test complete CRUD workflow for excluded keywords"""
        print("\n=== Testing full CRUD workflow ===")
        
        # 1. Check initial state (should be empty)
        response = await self.client.get('/api/excluded_keywords')
        data = await response.get_json()
        initial_count = len(data['keywords'])
        print(f"Initial keywords count: {initial_count}")
        
        # 2. Add multiple keywords
        test_keywords = ['интеграционный_тест', 'spam', 'test_keyword']
        for keyword in test_keywords:
            response = await self.client.post(
                '/api/excluded_keywords',
                json={'keyword': keyword},
                headers={'Content-Type': 'application/json'}
            )
            assert response.status_code == 200
            print(f"Added keyword: {keyword}")
        
        # 3. Verify all keywords were added
        response = await self.client.get('/api/excluded_keywords')
        data = await response.get_json()
        assert len(data['keywords']) == initial_count + len(test_keywords)
        for keyword in test_keywords:
            assert keyword in data['keywords']
        print(f"Verified {len(test_keywords)} keywords added")
        
        # 4. Remove one keyword
        response = await self.client.delete('/api/excluded_keywords/spam')
        assert response.status_code == 200
        print("Removed keyword: spam")
        
        # 5. Verify keyword was removed
        response = await self.client.get('/api/excluded_keywords')
        data = await response.get_json()
        assert len(data['keywords']) == initial_count + len(test_keywords) - 1
        assert 'spam' not in data['keywords']
        assert 'интеграционный_тест' in data['keywords']
        assert 'test_keyword' in data['keywords']
        print("✓ Full CRUD workflow completed successfully")


async def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting integration tests for excluded keywords API...")
    print("=" * 60)
    
    test_instance = TestExcludedKeywordsAPI()
    
    test_methods = [
        'test_get_excluded_keywords_empty',
        'test_get_excluded_keywords_with_data',
        'test_get_excluded_keywords_unauthorized',
        'test_post_excluded_keyword_success',
        'test_post_excluded_keyword_empty',
        'test_post_excluded_keyword_whitespace',
        'test_post_excluded_keyword_duplicate',
        'test_post_excluded_keyword_unauthorized',
        'test_delete_excluded_keyword_success',
        'test_delete_excluded_keyword_not_found',
        'test_delete_excluded_keyword_unauthorized',
        'test_delete_excluded_keyword_with_spaces',
        'test_full_crud_workflow'
    ]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            print(f"\n🧪 Running {method_name}...")
            
            # Setup
            await test_instance.setup_method()
            
            # Run test
            method = getattr(test_instance, method_name)
            await method()
            
            # Teardown
            await test_instance.teardown_method()
            
            print(f"✅ {method_name} - PASSED")
            passed += 1
            
        except Exception as e:
            print(f"❌ {method_name} - FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    # Close database connection
    await db_manager.close()


if __name__ == '__main__':
    asyncio.run(run_all_tests())