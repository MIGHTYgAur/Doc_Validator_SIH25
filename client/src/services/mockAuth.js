// Mock authentication service
import ApiService from './ApiService';

export class MockAuthService {
  static currentUser = null;

  static async login(email, password, userType) {
    try {
      // Use ApiService for login
      const response = await ApiService.loginUser(email, password, userType);
      
      if (response.success) {
        this.currentUser = response.user;
        localStorage.setItem('mockUser', JSON.stringify(response.user));
        return { success: true, user: response.user };
      }
      
      return { success: false, error: 'Invalid credentials' };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed' };
    }
  }

  static async register(userData) {
    try {
      // Use ApiService for registration
      const response = await ApiService.createUser(userData);
      
      if (response.success) {
        this.currentUser = response.user;
        localStorage.setItem('mockUser', JSON.stringify(response.user));
        return { success: true, user: response.user };
      }
      
      return { success: false, error: 'Registration failed' };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration failed' };
    }
  }

  static logout() {
    this.currentUser = null;
    localStorage.removeItem('mockUser');
  }

  static getCurrentUser() {
    if (this.currentUser) return this.currentUser;
    
    const stored = localStorage.getItem('mockUser');
    if (stored) {
      this.currentUser = JSON.parse(stored);
      return this.currentUser;
    }
    
    return null;
  }

  static isAuthenticated() {
    return this.getCurrentUser() !== null;
  }
}