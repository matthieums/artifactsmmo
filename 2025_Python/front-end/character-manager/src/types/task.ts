export interface Task {
  taskName: string;
  iterations: number
  kwargs?: {
    resource?: string;
    location?: string;
    quantity?: number;
  };
};

export type TaskQueue = {
  [characterName: string]: Task[];
};