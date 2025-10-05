// Simple test to verify authentication endpoints
import { API_URLS } from '../constants/serverConfig';

// Test function to verify backend connectivity
export const testBackendConnection = async () => {
  try {
    // Test health endpoint first
    const healthResponse = await fetch(API_URLS.HEALTH);
    console.log('Health check:', healthResponse.status);
    
    // Test auth endpoints exist (should return 422 for missing data)
    const loginResponse = await fetch(API_URLS.LOGIN, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    console.log('Login endpoint test:', loginResponse.status);
    
    const registerResponse = await fetch(API_URLS.REGISTER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    console.log('Register endpoint test:', registerResponse.status);
    
    return {
      health: healthResponse.status,
      login: loginResponse.status,
      register: registerResponse.status
    };
  } catch (error) {
    console.error('Backend connection test failed:', error);
    return { error: error instanceof Error ? error.message : 'Unknown error' };
  }
};

// Test authentication flow
export const testAuthFlow = async () => {
  const testUser = {
    email: 'test@example.com',
    password: 'testpassword123',
    full_name: 'Test User'
  };
  
  try {
    // Try to register
    const registerResponse = await fetch(API_URLS.REGISTER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testUser)
    });
    
    console.log('Register test:', registerResponse.status);
    
    if (registerResponse.ok) {
      const user = await registerResponse.json();
      console.log('User created:', user);
      
      // Try to login
      const loginResponse = await fetch(API_URLS.LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: testUser.email,
          password: testUser.password
        })
      });
      
      console.log('Login test:', loginResponse.status);
      
      if (loginResponse.ok) {
        const token = await loginResponse.json();
        console.log('Token received:', token);
        return { success: true, token };
      }
    }
    
    return { success: false, register: registerResponse.status };
  } catch (error) {
    console.error('Auth flow test failed:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
};
