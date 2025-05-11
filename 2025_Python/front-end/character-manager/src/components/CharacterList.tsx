import React, { useState, useEffect } from "react";
import { AddTask } from "./AddTask";
import { TaskQueueViewer } from "./TaskQueueViewer";
import { Task, TaskQueue } from "../types/task";
import { CharactersDict } from "../types/character";
import { CharacterImage } from "./CharacterImage";
import { apiFetch } from "../utils"


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
                const data = await apiFetch("/task_queues");
                setTaskQueues(data);
            } catch(err) {
                console.error("Error while fetching task queue", err);
            }
        }
        
        const fetchCharacters = async () => {
            try {
                const data = await apiFetch("/characters");
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
            <div key={char.name}>{char.name}
                <CharacterImage source={`https://artifactsmmo.com/images/characters/${char.skin}.png/`} />
                 <div>{`${char.ongoing_task}..`}</div>
                    <div>
                        {tasks.map((t, i) => (
                            <AddTask
                            key={i}
                            characterName={char.name}
                            taskName={t.taskName}
                            kwargs={t.kwargs}
                            />
                        ))}
                    </div>
                <div>
                    <TaskQueueViewer queue={taskQueues[char.name]}/>
                </div>
            </div>
            ))}

        </div>
    );
}


