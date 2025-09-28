import ApiService from './ApiService';

class AuthService {
  static currentUser = null;

  // Register new user
  static async register(userData) {
    try {
      const response = await ApiService.registerUser(userData);
      
      // Auto-login after successful registration
      const userType = userData.userType || userData.userRole; // Handle both keys
      const loginResponse = await this.login(userData.email, userData.password, userType);
      return loginResponse;
      
    } catch (error) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: error.message || 'Registration failed' 
      };
    }
  }

  // Login user
  static async login(email, password, userType) {
    try {
      const response = await ApiService.loginUser(email, password, userType);
      
      if (response.user) {
        // Convert backend response to frontend format
        const user = {
          id: response.user.id,
          name: response.user.name,
          email: response.user.email,
          userType: response.role, // role -> userType for frontend
          institution: response.user.institution,
          token: response.access_token
        };
        
        // Store user data
        this.currentUser = user;
        localStorage.setItem('currentUser', JSON.stringify(user));
        
        return { success: true, user };
      } else {
        return { 
          success: false, 
          error: 'Invalid login response' 
        };
      }
      
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.message || 'Login failed' 
      };
    }
  }

  // Get current user
  static getCurrentUser() {
    if (this.currentUser) {
      return this.currentUser;
    }
    
    // Try to get from localStorage
    const stored = localStorage.getItem('currentUser');
    if (stored) {
      try {
        this.currentUser = JSON.parse(stored);
        return this.currentUser;
      } catch (e) {
        console.error('Failed to parse stored user data:', e);
        localStorage.removeItem('currentUser');
      }
    }
    
    return null;
  }

  // Logout user
  static logout() {
    this.currentUser = null;
    localStorage.removeItem('currentUser');
  }

  // Check if user is logged in
  static isLoggedIn() {
    return this.getCurrentUser() !== null;
  }
}

export { AuthService };