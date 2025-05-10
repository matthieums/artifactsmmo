import React, { useState, useEffect } from "react";
import { AddTask } from "./AddTask";

interface Character {
  id: number;
  name: string;
  ongoing_task: string;
}

type CharactersDict = { [name: string]: Character };

export function CharacterList() {
    const [characters, setCharacters] = useState<CharactersDict>({});

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
                    <AddTask characterName={char.name} />
                    </li>
                ))}
                </ul>
           </div>
       </div>
    );
}


