import React, { useState, useEffect } from "react";
import { AddTask } from "./AddTask";

interface Character {
  id: number;
  name: string;
}

export function CharacterList() {
    const [characters, setCharacters] = useState<Character[]>([]);
    
    useEffect(() => {
        let interval: NodeJS.Timeout;

        async function fetchCharacters() {
            try {
                const response = await fetch("http://127.0.0.1:8000/");
                const data = await response.json();
                setCharacters(data);
                
                if (data.length > 0) {
                    clearInterval(interval);
                }
            } catch (err) {
                console.error("Error fetching characters:", err);
            }
        }

        fetchCharacters();
        interval = setInterval(fetchCharacters, 5000);
        
        return () => 
            {
                clearInterval(interval)
            };
    }, []);


    return (
       <div>
           <div>
               <h3>Characters:</h3>
                <ul>
                    {characters.map((char, index) => (
                        <li key={index}>
                            {char.name}
                            < AddTask characterIndex={index}/>
                        </li>
                    ))}
                </ul>
           </div>
       </div>
    );
}


