const fetch = require('node-fetch');

// Test URLs
const urls = [
  'http://localhost:8080',
  'https://sentinalai-production.up.railway.app',
  'https://thrush-real-lacewing.ngrok-free.app'
];

async function testConnection(url) {
  console.log(`\n=== Testing ${url} ===`);
  
  try {
    console.log(`Making request to: ${url}/health`);
    const startTime = Date.now();
    
    const response = await fetch(`${url}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      timeout: 10000
    });
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    console.log(`Response: ${response.status} ${response.statusText}`);
    console.log(`Duration: ${duration}ms`);
    console.log(`Headers:`, Object.fromEntries(response.headers.entries()));
    
    if (response.ok) {
      const text = await response.text();
      console.log(`Body: ${text}`);
    }
    
    return response.ok;
  } catch (error) {
    console.log(`Error: ${error.message}`);
    console.log(`Error type: ${error.constructor.name}`);
    if (error.code) console.log(`Error code: ${error.code}`);
    return false;
  }
}

async function runTests() {
  console.log('=== Connection Test Suite ===');
  console.log('Testing backend connectivity from mobile app perspective...\n');
  
  for (const url of urls) {
    const success = await testConnection(url);
    console.log(`Result: ${success ? 'SUCCESS' : 'FAILED'}`);
  }
  
  console.log('\n=== Test Complete ===');
}

runTests().catch(console.error); 