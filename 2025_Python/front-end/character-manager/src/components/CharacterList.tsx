import React, { useState, useEffect } from "react";
import { AddTask } from "./AddTask";
import { TaskQueueViewer } from "./TaskQueueViewer";
import { Task, TaskQueue } from "../types/task";
import { CharactersDict } from "../types/character";
import { CharacterImage } from "./CharacterImage";

export function CharacterList() {
    const [characters, setCharacters] = useState<CharactersDict>({});
    const [taskQueues, setTaskQueues] = useState<TaskQueue>({});

    const tasks: Task[] = [
        {taskName: "fight", iterations: 1, kwargs: { location: "chicken" }},
        {taskName: "gather", iterations: 1, kwargs: { resource: "copper_ore" }}
    ]

    useEffect(() => {
        const fetchTaskQueues = async () => {
            try {
                const response = await fetch("http://127.0.0.1:8000/task_queues");
                const data = await response.json();
                setTaskQueues(data);
            } catch(err) {
                console.error("Error while fetching task queue", err);
            }
        }
        
        const fetchCharacters = async () => {
            try {
                const response = await fetch("http://127.0.0.1:8000/characters");
                const data = await response.json();
                setCharacters(data);
            } catch (err) {
                console.error("Error fetching characters:", err);
            }
        }
        
        fetchCharacters();
        fetchTaskQueues();

        const interval = setInterval(() => {
            fetchCharacters();
            fetchTaskQueues();
        }, 5000);

        return () => clearInterval(interval);
        }, []);

    return (
       <div>
            <div>
                <h3>Characters:</h3>
            </div>
            {Object.values(characters).map((char) => (
            <div key={char.name}>
                <CharacterImage source={`https://artifactsmmo.com/images/characters/${char.skin}.png/`} />
                {char.name} - {`${char.ongoing_task}..`}
                    <input type="number" />
                    {tasks.map((t, i) => (
                        <AddTask 
                        key={i}
                        iterations={2}
                        characterName={char.name}
                        taskName={t.taskName}
                        kwargs={t.kwargs}
                        />
                    ))}
                    <div>
                        <TaskQueueViewer queue={taskQueues[char.name]}/>
                    </div>
            </div>
            ))}

        </div>
    );
}


