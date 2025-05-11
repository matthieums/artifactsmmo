export interface Character {
  id: number;
  name: string;
  ongoing_task: string;
}

export type CharactersDict = { [name: string]: Character };