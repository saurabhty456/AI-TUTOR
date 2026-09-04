export type User = {
  id: number;
  name: string;
  email: string;
  created_at: string;
};

export type Credentials = {
  email: string;
  password: string;
};

export type SignupDetails = Credentials & {
  name: string;
};
