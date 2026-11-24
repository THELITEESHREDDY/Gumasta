export interface User {
  id: string;
  name: string;
  email: string;
  mobile: string;
  created_at: string;
}

export interface RegisterData {
  name: string;
  email: string;
  mobile: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}