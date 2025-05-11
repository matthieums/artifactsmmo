export interface Character {
  id: number;
  name: string;
  ongoing_task: string;
  skin: string;
}

export type CharactersDict = { [name: string]: Character };