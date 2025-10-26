
export interface Source {
  uri: string;
  title: string;
}

export interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  sources?: Source[];
}
