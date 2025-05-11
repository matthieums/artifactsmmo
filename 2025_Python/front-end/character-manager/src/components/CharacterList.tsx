import React, { useState, useEffect } from "react";
import { AddTask } from "./AddTask";

interface Character {
  id: number;
  name: string;
  ongoing_task: string;
}

type CharactersDict = { [name: string]: Character };

type Task = {
  taskName: string;
  iterations: number
  kwargs: {
    resource?: string;
    location?: string;
    quantity?: number;
  };
};

export function CharacterList() {
    const [characters, setCharacters] = useState<CharactersDict>({});
    const tasks: Task[] = [
        {taskName: "fight", iterations: 1, kwargs: { location: "chicken" }},
        {taskName: "gather", iterations: 1, kwargs: { resource: "copper_ore" }}
    ]
    useEffect(() => {
        let interval: NodeJS.Timeout;

        async function fetchCharacters() {
            try {
                const response = await fetch("http://127.0.0.1:8000/");
                const data = await response.json();
                setCharacters(data);
                
            } catch (err) {
                console.error("Error fetching characters:", err);
            }
        }

        fetchCharacters();
        interval = setInterval(fetchCharacters, 5000);
        
        return () => { clearInterval(interval) };
    }, []);


    return (
       <div>
           <div>
               <h3>Characters:</h3>
                <ul>
                {Object.values(characters).map((char, index) => (
                    <li key={index}>
                        {char.name} - {char.ongoing_task}
                        {tasks.map((t, i) => (
                            <AddTask 
                                key={i}
                                iterations={2}
                                characterName={char.name}
                                taskName={t.taskName}
                                kwargs={t.kwargs}
                            />
                        ))}
                    </li>
                ))}
                </ul>
           </div>
       </div>
    );
}


