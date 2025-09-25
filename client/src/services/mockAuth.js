// Mock authentication service
export class MockAuthService {
  static currentUser = null;

  static login(email, password, userType) {
    // Mock validation - accepts any credentials
    if (email && password) {
      const user = {
        id: Math.random().toString(36).substr(2, 9),
        email: email,
        name: email.split('@')[0],
        userType: userType, // 'issuer' or 'verifier'
        loginTime: new Date().toISOString()
      };
      
      this.currentUser = user;
      localStorage.setItem('mockUser', JSON.stringify(user));
      return { success: true, user };
    }
    
    return { success: false, error: 'Invalid credentials' };
  }

  static register(userData) {
    // Mock registration - accepts any data
    const user = {
      id: Math.random().toString(36).substr(2, 9),
      ...userData,
      registeredAt: new Date().toISOString()
    };
    
    this.currentUser = user;
    localStorage.setItem('mockUser', JSON.stringify(user));
    return { success: true, user };
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