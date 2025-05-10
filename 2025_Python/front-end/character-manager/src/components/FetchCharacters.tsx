import React, { useState } from "react";

interface Character {
  id: number;
  name: string;
}

export function FetchCharacters() {
    const [characters, setCharacters] = useState<Character[]>([])
    async function handleClick() {
        try {
            const response = await fetch("http://127.0.0.1:8000/");
            
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            
            const data = await response.json();
            
            setCharacters(data);
        } catch (error) {
            console.error("Error fetching characters:", error);
        }
    }
    return (
        <div>
            <button onClick={handleClick}>Fetch
            </button>
            <div>
                <h3>Fetched characters:</h3>
                    <ul>
                        {characters.length > 0 ? (
                            characters.map((char, index) => (
                                <li key={index}>
                                    {char.name}
                                </li>
                            ))
                        ) : (
                            <p>No characters found.</p>
                        )}
                    </ul>
            </div>
        </div>
    )
}


