import { API_URLS } from '../constants/serverConfig';

export interface User {
  id: number;
  email: string;
  full_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export class AuthService {
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    console.log(API_URLS.LOGIN);
    const response = await fetch(API_URLS.LOGIN, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  static async signup(userData: SignupRequest): Promise<User> {
    const response = await fetch(API_URLS.REGISTER, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }

    return response.json();
  }

  static setToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  static getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  static removeToken(): void {
    localStorage.removeItem('access_token');
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Helper method to make authenticated requests
  static async authenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    if (!token) {
      throw new Error('No authentication token found');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    };

    return fetch(url, {
      ...options,
      headers,
    });
  }
}
